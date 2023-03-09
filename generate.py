import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

DEFAULT_EC_CURVE = ec.SECP384R1()
EC_CURVE_NAMES = {
    256: "P-256",
    384: "P-384",
    521: "P-512",
}
SIGNING_ALGORITHMS = {
    256: "ES256",
    384: "ES384",
    521: "ES512",
}


def die(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def convert_key(public_key, **options):
    numbers = public_key.public_numbers()
    size = (numbers.curve.key_size + 7) // 8
    x = numbers.x.to_bytes(size, "big")
    y = numbers.y.to_bytes(size, "big")
    return {
        "kty": "EC",
        "crv": EC_CURVE_NAMES[numbers.curve.key_size],
        "x": base64.urlsafe_b64encode(x).decode("ascii"),
        "y": base64.urlsafe_b64encode(y).decode("ascii"),
        **options,
    }


def key_fingerprint(public_key):
    der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def infer_issuer():
    p = subprocess.run(
        ["git", "remote", "--verbose"], check=True, capture_output=True, text=True
    )
    for l in p.stdout.splitlines():
        m = re.search("github.com[/|:](.+?)/(.+?)(.git)? \((fetch|push)\)", l)
        if m is not None:
            owner = m.group(1)
            repo = m.group(2)

            if repo == f"{owner}.github.io":
                return f"did:web:{owner}.github.io"
            else:
                return f"did:web:{owner}.github.io:{repo}"
    else:
        die("Error: could not infer a DID from the git configuration")


def main():
    if len(sys.argv) == 1:
        did = infer_issuer()
    elif len(sys.argv) == 2:
        did = sys.argv[1]
        if not did.startswith("did:web:"):
            die(f"Error: `{did}` is not a valid did:web")
    else:
        die(f"Usage:\n  {sys.argv[0]}\n  {sys.argv[0]} did:web:example.com")

    private_key_path = Path("private_key.pem")
    if private_key_path.exists():
        print(f"Using existing private key at `{private_key_path}`")
        private_key = serialization.load_pem_private_key(
            private_key_path.read_bytes(), None
        )
        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            die("Error: Only EC keys are supported")

    else:
        private_key = ec.generate_private_key(ec.SECP384R1())

        print(f"Writing new private key to `{private_key_path}`")
        private_key_path.write_bytes(
            private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

    public_key = private_key.public_key()

    kid = "#" + key_fingerprint(public_key)

    print(f"Creating a new DID document for `{did}`...")

    document = {
        "id": did,
        "assertionMethod": [
            {
                "id": f"{did}{kid}",
                "type": "JsonWebKey2020",
                "controller": did,
                "publicKeyJwk": convert_key(
                    public_key,
                    kid=kid,
                    alg=SIGNING_ALGORITHMS[public_key.key_size],
                ),
            }
        ],
    }

    with open("docs/did.json", "w") as f:
        json.dump(document, f, indent=2)

    subprocess.run(["git", "add", "docs/did.json"], check=True)

    p = subprocess.run(["git", "diff-index", "--quiet", "HEAD", "docs/did.json"])
    if p.returncode > 0:
        print("Committing the DID document...")
        subprocess.run(
            [
                "git",
                "commit",
                "--quiet",
                "--allow-empty",
                "docs/did.json",
                "-m",
                "Updating DID document",
            ],
            check=True,
        )

    print("Done!")
    print("Run `git push` to publish the new DID document to GitHub")
    print(
        f"After pushing, you may check its status at https://dev.uniresolver.io/#{did}"
    )


main()
