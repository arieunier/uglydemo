create table public.badge(id varchar(255) not null primary key, guest_id varchar(255) not null, guest_firstname varchar(255) not null, guest_lastname varchar(255) not null,
        guest_company varchar(255), host_firstname varchar(255) not null, host_lastname varchar(255) not null, badge_status varchar(255), badge_url varchar(255), creation_date timestamp not null)
