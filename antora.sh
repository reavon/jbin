#!/usr/bin/env bash

mkdir -p modules/ROOT/{attachments,examples,images,pages,partials}
touch modules/ROOT/{attachments,examples,images,pages,partials}/.gitkeep
touch modules/ROOT/nav.adoc

mkdir -p modules/another-module/{attachments,examples,images,pages,partials}
touch modules/another-module/{attachments,examples,images,pages,partials}/.gitkeep

touch README.adoc
touch antora.yml
