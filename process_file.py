import os, json, boto3
import psycopg2
from botocore.exceptions import ClientError

def get_db_creds(secret_arn):
    sm = boto3.client("secretsmanager")
    return json.loads(sm.get_secret_value(SecretId=secret_arn)["SecretString"])

def main():
    bucket = os.environ["S3_INPUT_BUCKET"]
    key = os.environ["S3_INPUT_KEY"]
    secret_arn = os.environ["DB_SECRET_ARN"]

    s3 = boto3.client("s3")
    local = "/tmp/input.pdf"
    s3.download_file(bucket, key, local)

    # --- YOUR OCR/A I WORK HERE ---
    # e.g. run tesseract or call a model, extract text lines:
    extracted_text = ["line1","line2"]

    # Write to Postgres
    creds = get_db_creds(secret_arn)
    conn = psycopg2.connect(host=creds["host"], dbname=creds["dbname"],
                            user=creds["username"], password=creds["password"])
    cur = conn.cursor()
    for line in extracted_text:
        cur.execute("INSERT INTO ocr_results (s3_key, text) VALUES (%s,%s)", (key, line))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
