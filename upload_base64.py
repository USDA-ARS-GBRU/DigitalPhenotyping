import base64

file = "sample.zip"
with open(file, 'rb') as f:
    encoded = base64.encodebytes(f.read())
    print(encoded)

# Linux command for extracting bytestring
# cat out.json | jq '.result.data[0].description' | xclip -selection clipboard

# with open("encoded_file", 'wb') as f:
#     f.write(encoded)

# with open("copy_output", 'rb') as f:
#     encoded = f.read().replace(b"\"", b"").replace(b"\\n", b"\n")

# with open("encoded_file", 'w') as f:
#     f.write(encoded.decode('utf-8'))

# with open("encoded_file", 'rb') as f:
#     encoded = f.read()

# with open("decode_outfile.zip", 'wb') as f:
#     decoded = base64.b64decode(encoded)
#     f.write(decoded)
