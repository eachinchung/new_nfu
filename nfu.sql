use nfu;

create table user
(
    id          int(9)       not null primary key,
    name        varchar(15)  not null,
    password    char(94)     not null,
    room_id     int(8)       not null,
    email       varchar(255) not null,
    bus_session varchar(50)  null
);

create table power
(
    id             int(9)     not null primary key,
    validate_email tinyint(1) not null,
    bus_ticket     tinyint(1) not null,
    admin          tinyint(1) not null,
    foreign key (id) references user (id) on delete cascade on update cascade
);

create table dormitory
(
    id       int(8)  not null primary key,
    building char(15) not null,
    floor    char(2) not null,
    room     int(3)  not null
);

create table electric
(
    id      int primary key auto_increment,
    room_id int(8) not null,
    value   float  not null,
    time    date   not null,
    index room_id (room_id)
);

create table total_achievements
(
    id                        int(9) not null primary key,
    get_credit                int    not null,
    selected_credit           int    not null,
    average_achievement       float  not null,
    average_achievement_point float  not null,
    foreign key (id) references user (id) on delete cascade on update cascade
);

create table achievement
(
    id                     int primary key auto_increment,
    user_id                int(9)      not null,
    course_type            char(15)    not null,
    course_name            varchar(50) not null,
    course_id              varchar(50) not null,
    resit_exam             tinyint(1)  not null,
    credit                 float       not null,
    achievement_point      float       not null,
    final_achievements     float       not null,
    total_achievements     float       not null,
    midterm_achievements   float       not null,
    practice_achievements  float       not null,
    peacetime_achievements float       not null,
    foreign key (user_id) references user (id) on delete cascade on update cascade
);

create table class_schedule
(
    id          int         not null primary key auto_increment,
    user_id     int(9)      not null,
    course_name varchar(50) not null,
    course_id   varchar(50) not null,
    teacher     char(25)    not null,
    classroom   char(25)    not null,
    weekday     tinyint     not null,
    start_node  tinyint     not null,
    end_node    tinyint     not null,
    start_week  tinyint     not null,
    end_week    tinyint     not null,
    foreign key (user_id) references user (id) on delete cascade on update cascade
);

create table ticket_order
(
    id            int          not null primary key auto_increment,
    user_id       int(9)       not null,
    ticket_time   datetime     not null,
    bus_ids       json         not null,
    passenger_ids json         not null,
    order_message varchar(255) not null,
    order_time    datetime     not null,
    trade_no      varchar(50)  null,
    foreign key (user_id) references user (id) on delete cascade on update cascade
);

alter table ticket_order
    auto_increment = 1000000000;