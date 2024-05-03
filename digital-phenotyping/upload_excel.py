from typing import List
import requests
from bs4 import BeautifulSoup
import urllib
import json


def get_trait_list(s: requests.Session) -> List[str]:
    get_traits_to_delete_url = "https://demo.breedbase.org/ajax/html/select/traits?name=retrieve_assayed_trial_traits_select&id=retrieve_assayed_trial_traits_select&trial_ids=167&size=20px&multiple=1"
    res = s.get(get_traits_to_delete_url)

    soup = BeautifulSoup(res.json()['select'], "html.parser")
    return [option['value'] for option in soup.find_all("option")]


def delete_traits(s: requests.Session, traits):
    delete_url = "https://demo.breedbase.org/ajax/breeders/trial/167/delete_single_trait"
    url_encoded_traits = urllib.parse.urlencode(
        {"traits": json.dumps(traits, separators=(',', ':'))})
    res = s.post(delete_url, data=url_encoded_traits, headers={
                 "Content-Type": 'application/x-www-form-urlencoded'})
    print(res.request.body)
    print(res.json())




def get_upload_spreadsheet(s: requests.Session, trial_id, trait_list):
    url = "https://demo.breedbase.org/ajax/phenotype/create_spreadsheet"
    url_encoded_data = urllib.parse.urlencode({
        "trait_ids": json.dumps([trial_id], separators=(',', ':')),
        "trait_list": json.dumps(trait_list, separators=(',', ':')),
        "include_notes": "false",
        "data_levels": "plots",
        "sample_number": "",
        "format": "ExcelBasicSimple",
        "trial_stock_type": "accession"
    })
    res = s.post(url, data=url_encoded_data, headers={
                 "Content-Type": 'application/x-www-form-urlencoded',
                 "Origin": "https://demo.breedbase.org", 
                 "Referer": 'https://demo.breedbase.org/breeders/trial/167?', 
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"})
    print(res.request.body)
    print(res.request.headers)
    # print(res.text)
    with open("dump.html", "w") as f:
        f.write(res.text)


if __name__ == "__main__":
    login_url = f"https://demo.breedbase.org/ajax/user/login?username=janedoe&password=secretpw"
    with requests.Session() as s:
        res = s.get(login_url)
        # traits = get_trait_list(s)
        # print(traits)
        # delete_traits(s, traits)
        get_upload_spreadsheet(s, 167, ["CO_334:0000008", "CO_334:0000009", "CO_334:0000010", "CO_334:0000011",
                               "CO_334:0000012", "CO_334:0000013", "CO_334:0000014", "CO_334:0000015", "CO_334:0000016", "CO_334:0000017"])
