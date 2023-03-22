# did:web generation sample using GitHub Pages

This repository provides a simplified process for creating your own
[decentralized identifier (or DID)](did-core), using [the `did:web`
method](did-method-web). It generates a new key pair and creates a DID
document which uses the public key as an `assertionMethod`.

The document will be hosted on GitHub pages, and the DID will have the
form `did:web:github.io:USERNAME:did-web-demo`.

## Instructions
1. Fork this repository under your own GitHub user

2. Clone your fork to your local machine:
   ```sh
   git clone https://github.com/USERNAME/did-web-demo
   # Or, if you prefer SSH-based authentication
   git clone git@github.com:USERNAME/did-web-demo.git
   ```

3. In a terminal, navigate to the cloned repository and run the `generate.sh` script:
   ```sh
   cd did-web-demo
   ./generate.sh
   ```

4. Push the repository to publish the newly created DID document
   ```sh
   git push
   ```

5. After a few minutes, the DID should be ready to be used. You may try an
   online resolver such as [uniresolver.io][uniresolver], using the DID that was
   printed to your console.

6. The `generate.sh` script will have created a `private_key.pem` file in the
   current directory. This file is not published to GitHub, and should be kept
   secret. It can be used anywhere control of the newly created DID needs to be
   asserted.

## Dependencies

The instructions above should work on macOS and any Linux distribution, or any
other POSIX-like environment. Windows users can run the `generate.sh` using
WSL. Additionally, the git command and a Python 3 interpreter must be
available.

[did-core]: https://www.w3.org/TR/did-core/
[did-method-web]: https://w3c-ccg.github.io/did-method-web/
[uniresolver]: https://dev.uniresolver.io/
