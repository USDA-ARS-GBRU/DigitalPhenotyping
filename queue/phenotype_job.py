import requests
import json
import os
from requests_toolbelt import MultipartEncoder
from transcribe import transcribe
from phenotype import link_plants
import xlsxwriter


def process_job(data):
    login_url = f"https://demo.breedbase.org/ajax/user/login?username=janedoe&password=secretpw"
    brapi_login_url = "https://demo.breedbase.org/brapi/v2/token?username=janedoe&password=secretpw"
    brapi_list_assections_url = f"https://demo.breedbase.org/brapi/v2/observationunits?studyDbId=167&observationUnitLevelName=plot"
    brapi_trait_names_url = f"https://demo.breedbase.org/brapi/v2/lists/13"
    brapi_variables_url = f"https://demo.breedbase.org/brapi/v2/variables/?pageSize=300"
    verify_spreadsheet_url = "https://demo.breedbase.org/ajax/phenotype/upload_verify/spreadsheet"
    upload_url = f"https://demo.breedbase.org/ajax/breeders/trial/{data['field_id']}/upload_additional_file"
    observations_output_url = f"https://demo.breedbase.org/brapi/v2/observations"
    file_path = "../1689174780836.wav"
    with requests.Session() as s:
        with requests.Session() as s_brapi:
            res = s.get(login_url)
            res = s_brapi.get(brapi_login_url)
            access_token = res.json().get("access_token")

            with s.get(data["audio_url"], stream=True) as r:
                r.raise_for_status()
                filename = r.headers.get(
                    "Content-Disposition").split("filename=")[1][1:-1]
                with open("tmp.mp3", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            with s.get(data["log_url"], stream=True) as r:
                r.raise_for_status()
                log_filename = r.headers.get(
                    "Content-Disposition").split("filename=")[1][1:-1]
                log_filename = log_filename.replace(":", "_")
                with open(log_filename.replace(":", "_"), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Process file TODO add timestamp extraction
            # transcript = transcribe("tmp.mp3")
            # TODO remove after testing
            transcript = transcribe("../1689176449522.wav")
            print(transcript)
            plant_features: dict = link_plants(transcript, log_filename)
            print(plant_features)


            # Get list of assessions
            accessions = s.get(brapi_list_assections_url)
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
            trait_names = s.get(brapi_trait_names_url)
            trait_names = trait_names.json()['result']['data']
            print(trait_names)

            # MODULE 1: Spreadsheet uploader
            
            # # TODO (fix the linking) Cross-check linked plant features with assession list
            tmp = list(plant_features.keys())
            for i, key in enumerate(tmp):
                plant_features[accessions[i]] = plant_features[key]
                del plant_features[key]
            print(plant_features)

            # # Create Spreasheet TODO (fix linking)
            with xlsxwriter.Workbook('phenotype_upload.xlsx') as workbook:
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
            with open("phenotype_upload.json", "w") as f:
                json.dump(plant_features, f)

            # # Upload json and xlsx files
            # m = MultipartEncoder(
            #     fields={'trial_upload_additional_file': (
            #         "phenotype_upload.xlsx", open(file_path, 'rb'))}
            # )

            # res = s.post(upload_url, data=m, headers={
            #     'Content-Type': m.content_type})
            # print(res, res.json())

            # m = MultipartEncoder(
            #     fields={'trial_upload_additional_file': (
            #         "phenotype_upload.json", open(file_path, 'rb'))}
            # )

            # res = s.post(upload_url, data=m, headers={
            #     'Content-Type': m.content_type})
            # print(res, res.json())

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
                        # "value": value[0].replace(" ", "_")
                        "value": 191
                    })

            print(json.dumps(observations_output))

            res = s_brapi.post(observations_output_url, json=observations_output, headers={
                               "Authorization": f"Bearer {access_token}"})  
            print(res, res.json())



if __name__ == "__main__":
    data = {
        'audio_url': 'https://demo.breedbase.org/breeders/phenotyping/download/42',
        'log_url': 'https://demo.breedbase.org/breeders/phenotyping/download/54',
        'field_id': 167,
        'file_id': 42,
        'debug': False
    }
    process_job(data)
