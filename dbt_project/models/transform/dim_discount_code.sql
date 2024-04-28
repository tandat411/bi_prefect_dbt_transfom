with source_data as (
    select dc_id as id,
        cus_id as seller_id,
        dc_code as code,
        dc_event as event,
        dc_amount as amount,
        case when dc_status = true 
			then 'Đã sử dụng'
            else 'Code chưa dùng'
        end as status,
        case when dc_created_time <> 0 
            then to_timestamp(dc_created_time)
            else NULL
        end as created_time,
        case when dc_start_time <> 0 
            then to_timestamp(dc_start_time)
            else NULL
        end as start_time,
        case when dc_end_time <> 0 
            then to_timestamp(dc_end_time)
            else NULL
        end as end_time,
        case when dc_use_time <> 0 
            then to_timestamp(dc_use_time)
            else NULL
        end as use_time,
        dc_deleted as deleted
    from {{ source('postgres', 'nh_discount_code') }}
)

select *
from source_data