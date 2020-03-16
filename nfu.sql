create database nfu;

use nfu;

create table user
(
    id       int unsigned not null primary key,
    name     varchar(15)  not null,
    password char(94)     not null,
    room_id  int          not null,
    email    varchar(255) not null
);

create table bus_user
(
    user_id        int unsigned not null primary key,
    alipay_user_id varchar(20)  not null,
    id_card        varchar(20)  not null,
    bus_session    varchar(50)
);

create table dormitory
(
    id       int      not null primary key,
    building char(15) not null,
    floor    char(2)  not null,
    room     int      not null
);

create table electric
(
    id      bigint unsigned primary key auto_increment,
    room_id int  not null,
    value   float,
    date    date not null,
    index room_id (room_id)
);

create table total_achievements
(
    user_id                   int unsigned not null primary key,
    get_credit                int          not null,
    selected_credit           int          not null,
    average_achievement       float        not null,
    average_achievement_point float        not null,
    foreign key (user_id) references user (id) on delete cascade on update cascade
);

create table achievement
(
    id                           bigint unsigned primary key auto_increment,
    user_id                      int unsigned not null,
    school_year                  int          not null,
    semester                     tinyint      not null,
    course_type                  varchar(20)  not null,
    subdivision_type             varchar(20)  not null,
    course_name                  varchar(50)  not null,
    course_id                    varchar(50)  not null,
    credit                       float        not null,
    achievement_point            float        not null,
    final_achievements           float        not null,
    total_achievements           float        not null,
    midterm_achievements         float        not null,
    practice_achievements        float        not null,
    peacetime_achievements       float        not null,
    resit_exam_achievement_point float        null,
    index course_id (course_id),
    foreign key (user_id) references user (id) on delete cascade on update cascade
);

create table class_schedule
(
    id               bigint unsigned not null primary key auto_increment,
    user_id          int unsigned    not null,
    school_year      int             not null,
    semester         tinyint         not null,
    subdivision_type varchar(20)     not null,
    course_name      varchar(50)     not null,
    course_id        varchar(50)     not null,
    credit           float           not null,
    teacher          json            not null,
    classroom        char(25)        not null,
    weekday          tinyint         not null,
    start_node       tinyint         not null,
    end_node         tinyint         not null,
    start_week       tinyint         not null,
    end_week         tinyint         not null,
    index course_id (course_id),
    foreign key (user_id) references user (id) on delete cascade on update cascade
);

create table ticket_order
(
    id            int unsigned not null primary key auto_increment,
    user_id       int unsigned not null,
    bus_ids       int          not null,
    bus_order_id  int          null,
    passenger_ids json         not null,
    order_id      char(20)     not null,
    order_type    tinyint      not null,
    order_time    datetime     not null,
    order_state   tinyint      not null,
    ticket_date   date         not null,
    index user_id (user_id),
    unique index order_id (order_id),
    foreign key (user_id) references user (id) on delete cascade on update cascade
);

create table profession
(
    id         int unsigned not null primary key,
    profession varchar(50)  null
);

create table college
(
    id      int unsigned not null primary key,
    college varchar(50)  null
);

create table profile
(
    user_id       int unsigned not null primary key,
    grade         int unsigned not null,
    college_id    int unsigned not null,
    profession_id int unsigned not null,
    direction     varchar(50)  null,
    foreign key (college_id) references college (id) on delete cascade on update cascade,
    foreign key (profession_id) references profession (id) on delete cascade on update cascade,
    foreign key (user_id) references user (id) on delete cascade on update cascade
);
