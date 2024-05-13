# TODO, FIXME...

## Blockchain

- [X] `Build_tx` move custom type_url messages editions to other file (sp_approval)
- [ ] Add broadcast mode to `blockchain_client.broadcast_raw_tx`
- [X] `convert_value_to_json` move custom type_url messages editions to other file
- [X] `get_signatures` move custom type_url messages editions to other file

## Storage Provider

- [ ] Find a way to not use the go library

## Greenfield

- [X] Implement `multi_transfer`
- [ ] Add pagination to feegrant `get_allowances`
- [ ] Add pagination to feegrant `get_allowances_by_granter`
- [ ] Add `content_type` enums for `CreateObjectOptions` and `PutObjectOptions`
- [ ] Implement test_claims
- [ ] Add positive test case for `test_mirror_object`, `test_mirror_bucket`, `test_mirror_group`
- [ ] Solve issues with the test cases `test_impeach_validator`, `test_unjail_validator`, `test_undelegate`, `test_begin_redelegate`
