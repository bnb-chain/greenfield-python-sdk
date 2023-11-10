Changelog
=========

0.4.0 - 2023-11-13
-------

- Upgrade dependencies
- Resolve issues
- Add new functions:
    - `Basic`:
        - `get_block_result_by_height`
        - `get_commit`
        - `get_status`
        - `get_syncing`
    - `Bucket`:
        - `get_bucket_meta`
        - `list_buckets_by_bucket_id`
        - `list_bucket_by_payment_account`
        - `migrate_bucket`
    - `Group`:
        - `list_groups_by_account`
        - `list_groups_by_group_id`
        - `list_group_members`
        - `list_groups_by_owner`
        - `renew_group_member`
    - `Object`:
        - `list_object_by_object_id`
    - `Payment`:
        - `get_all_payment_accounts`
        - `list_user_payment_accounts`
    - `Storage Provider`:
        - `get_global_sp_store_price`
        - `update_sp_status`
    - `Virtual Group`:
        - `get_virtual_group_family`

0.3.0 - 2023-10-23
-------

- Updated codebase to support Greenfield 1.0.0

0.2.0 - 2023-08-28
-------

- Updated codebase to support Greenfield 0.2.3
- Remove secp256k1 dependency
  
0.1.0 - 2023-08-25
-------

- Initial implementation of the Greenfield Python SDK
