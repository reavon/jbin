#!/bin/bash

export GNUPGHOME=~/gnupg-workspace

mkdir -p "$GNUPGHOME"

cd "$GNUPGHOME" || exit

wget -O "$GNUPGHOME/gpg.conf" https://raw.githubusercontent.com/drduh/config/master/gpg.conf

# Create Strong Passphrase
LC_ALL=C tr -dc '[:upper:]' < /dev/urandom | fold -w 24 | head -n1

# gpg --expert --full-generate-key

echo "(8) RSA (set your own capabilities)"
echo "(E) Toggle the encrypt capability"
echo "(S) Toggle the sign capability"
echo "(Q) Finished"
echo "Key is valid for? (0) 0"


# gpg --expert --edit-key $KEYID
