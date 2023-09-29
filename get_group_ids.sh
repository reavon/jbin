#!/usr/bin/env bash

identity_store=d-906778cfca
group_name=$1

aws identitystore list-groups --identity-store-id ${identity_store} \
                              --region us-east-1 \
                              --filters AttributePath=DisplayName,AttributeValue="${group_name}"@pennmutual.com
