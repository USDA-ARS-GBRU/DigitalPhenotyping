import requests
import json
import os
from requests_toolbelt import MultipartEncoder
from transcribe import transcribe
from phenotype import link_plants
import xlsxwriter
from dotenv import dotenv_values

config = dotenv_values(".env.demo_breedbase")
# config = dotenv_values(".env.sugarcane_breedbase")


def download_file(session, url, output_dir):
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        filename = r.headers.get(
            "Content-Disposition").split("filename=")[1][1:-1]
        # file_type = filename.split(".")[-1]
        filename = filename.replace(":", "_")
        with open(os.path.join(output_dir, filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return filename


def process_job(job_name, data):
    trial_number = int(data['field_id'])
    file_path = "../1689176449522.wav"
    job_id = job_name.split("job_")[-1]
    TMP_DIR = f"tmp/{job_id}/worker"

    os.makedirs(TMP_DIR, exist_ok=True)

    login_url = f"{config['BREEDBASE_URL']}/ajax/user/login?username={config['BREEDBASE_USER']}&password={config['BREEDBASE_PASSWORD']}"
    brapi_login_url = f"{config['BREEDBASE_URL']}/brapi/v2/token?username={config['BREEDBASE_USER']}&password={config['BREEDBASE_PASSWORD']}"
    brapi_list_accessions_url = f"{config['BREEDBASE_URL']}/brapi/v2/observationunits?studyDbId={trial_number}&observationUnitLevelName=plot"
    brapi_trait_names_url = f"{config['BREEDBASE_URL']}/brapi/v2/lists/13"
    brapi_variables_url = f"{config['BREEDBASE_URL']}/brapi/v2/variables/?pageSize=1000"
    verify_spreadsheet_url = f"{config['BREEDBASE_URL']}/ajax/phenotype/upload_verify/spreadsheet"
    store_spreadsheet_url = f"{config['BREEDBASE_URL']}/ajax/phenotype/upload_store/spreadsheet"
    upload_url = f"{config['BREEDBASE_URL']}/ajax/breeders/trial/{trial_number}/upload_additional_file"
    observations_output_url = f"{config['BREEDBASE_URL']}/brapi/v2/observations"

    with requests.Session() as s:
        with requests.Session() as s_brapi:
            res = s.get(login_url)
            res = s_brapi.get(brapi_login_url)
            access_token = res.json().get("access_token")

            audio_filename = download_file(s, data["audio_url"], TMP_DIR)
            log_filename = download_file(s, data['log_url'], TMP_DIR)

            try:
                trait_filename = download_file(s, data['trait_url'], TMP_DIR)
            except Exception:
                trait_filename = None
                print("Trait file download error", data['trait_url'])

            # Process file TODO add timestamp extraction
            # transcript = transcribe(os.path.join(TMP_DIR, audio_filename))
            # TODO remove after testing
            transcript = transcribe(file_path)
            print(transcript)
            plant_features: dict = link_plants(
                transcript, os.path.join(TMP_DIR, log_filename), None)
            # plant_features: dict = link_plants(
            #     transcript, os.path.join(TMP_DIR, log_filename), os.path.join(TMP_DIR, trait_filename))
            print(plant_features)

            # Get list of assessions
            accessions = s.get(brapi_list_accessions_url)
            tmp = []
            tmp2 = []
            for assess in accessions.json()['result']['data']:
                tmp.append(assess['observationUnitName'])
                tmp2.append(assess['observationUnitDbId'])
            accessions = tmp
            accessions_id = tmp2
            print(accessions)
            print(accessions_id)

            # Get trait names
            # TODO lists brapi url stopped working
            # trait_names = s_brapi.get(brapi_trait_names_url)
            list_url = "https://demo.breedbase.org/list/data?list_id=13"
            traits = s.get(list_url).json()['elements']
            print(traits)
            trait_names = []
            trait_ids = []
            for trait in traits:
                trait_ids.append(trait[0])
                trait_names.append(trait[1])

            # trait_names = trait_names.json()['result']['data']
            print(trait_names)

            # MODULE 1: Spreadsheet uploader

            # # TODO (fix the linking) Cross-check linked plant features with assession list
            tmp = list(plant_features.keys())
            for i, key in enumerate(tmp):
                plant_features[accessions[i]] = plant_features[key]
                del plant_features[key]
            print(plant_features)

            # # Create Spreasheet TODO (fix linking)
            with xlsxwriter.Workbook(os.path.join(TMP_DIR, 'phenotype_upload.xlsx')) as workbook:
                worksheet = workbook.add_worksheet()

                worksheet.write(0, 0, "observationunit_name")
                for i, key in enumerate(plant_features.keys()):
                    worksheet.write(i + 1, 0, key)

                for i, trait in enumerate(trait_names):
                    worksheet.write(0, i+1, trait)

                for i, (assesion, value) in enumerate(plant_features.items()):
                    features = value['features']
                    for j, (trait, value) in enumerate(features.items()):
                        worksheet.write(i+1, j+1, value[0])

            # # Create a raw features file for extra review
            with open(os.path.join(TMP_DIR, "phenotype_upload.json"), "w") as f:
                json.dump(plant_features, f)

            # Upload json and xlsx files
            m = MultipartEncoder(
                fields={'upload_spreadsheet_phenotype_file_input': (
                    "phenotype_upload.xlsx", open(os.path.join(TMP_DIR, 'phenotype_upload.xlsx'), 'rb')),
                    "upload_spreadsheet_phenotype_file_format": "simple",
                    "upload_spreadsheet_phenotype_data_level": "plots"
                }
            )

            res = s.post(store_spreadsheet_url, data=m, headers={
                'Content-Type': m.content_type})
            print(res, res.json())

            m = MultipartEncoder(
                fields={'trial_upload_additional_file': (
                    "phenotype_upload.json", open(os.path.join(TMP_DIR, 'phenotype_upload.json'), 'rb'))}
            )

            res = s.post(upload_url, data=m, headers={
                'Content-Type': m.content_type})
            print(res, res.json())

            # # Cleanup for json and xlsx files
            # if not data.get("debug", False):
            #     os.remove("phenotype_upload.xlsx")
            #     os.remove("phenotype_upload.json")

            # MODULE 2: Brapi upload

            # Get obeservation variables(traits)
            obs_variables = s.get(brapi_variables_url)
            tmp = []
            for variable in obs_variables.json()['result']['data']:
                for trait in trait_names:
                    if trait in variable.get('observationVariableName', ""):
                        tmp.append(variable.get("observationVariableDbId", ""))

            trait_var_ids = tmp
            print(trait_var_ids)

            observations_output = []
            for i, (assesion, value) in enumerate(plant_features.items()):
                features = value['features']
                for j, (trait, value) in enumerate(features.items()):
                    observations_output.append({
                        "observationUnitDbId": accessions_id[i],
                        "observationVariableDbId": trait_var_ids[j],
                        "value": value[0].replace(" ", "_")
                        # "value": 191
                    })

            print(json.dumps(observations_output))

            res = s_brapi.post(observations_output_url, json=observations_output, headers={
                               "Authorization": f"Bearer {access_token}"})
            print(res, res.json())


if __name__ == "__main__":
    data = {
        'audio_url': 'https://demo.breedbase.org/breeders/phenotyping/download/42',
        'log_url': 'https://demo.breedbase.org/breeders/phenotyping/download/54',
        'trait_url': 'https://demo.breedbase.org/breeders/phenotyping/download/248',
        'field_id': 167,
        'debug': False
    }
    process_job("job_sample", data)
