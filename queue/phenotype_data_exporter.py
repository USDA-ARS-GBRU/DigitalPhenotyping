import pandas as pd

def export_spreadsheet(feature_data, template_file):
    raw_export_file = "raw_extracted_data.xlsx"
    constructed_export_file = "extracted_data.xlsx"
    df = pd.DataFrame(feature_data)
    print(df)
    # df.to_excel(raw_export_file)

    out_df = pd.read_excel(template_file)
    # TODO add actual plot matching - waiting for final format and trial creation

    out_data = out_df[6:]
    print(out_data)

if __name__ == "__main__":
    data = {'13RPN00010': {'transcript': 'red green stem one pod', 'features': {'stem': {'red green'}, 'flowering': {'one pod'}}}, '13RPN00011': {'transcript': 'one pods not flowering plants not flowering', 'features': {'flowering': {'not flowering'}}}}
    template_file = "fieldbook template.xlsx"
    export_spreadsheet(data, template_file)