
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

with source_data as (
    select dc_id,
        cus_id,
        dc_code,
        dc_event,
        dc_amount,
        dc_status,
        dc_deleted,
        dc_end_time,
        dc_use_time,
        dc_start_time,
        dc_created_time 
    from {{ source('snowflake', 'nh_discount_code') }}
)

select *
from source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
