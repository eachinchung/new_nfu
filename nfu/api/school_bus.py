from flask import Blueprint, request, g, jsonify, render_template

from nfu.decorators import check_access_token, check_power_school_bus
from nfu.school_bus import get_bus_schedule, get_passenger_data

school_bus_bp = Blueprint('school_bus', __name__)


@school_bus_bp.route('/get_schedule', methods=['POST'])
@check_access_token
@check_power_school_bus
def get_schedule():
    """
    获取班车时刻表
    :return:
    """

    route_id = request.form.get('route_id')
    date = request.form.get('date')

    schedule = get_bus_schedule(route_id, date, g.user.bus_session)
    if not schedule[0]:
        return jsonify({'message': schedule[1]}), 500

    return jsonify({
        'message': 'success',
        'schedule': schedule[1],
    })


@school_bus_bp.route('/passenger/get')
@check_access_token
@check_power_school_bus
def get_passenger():
    """
    获取乘车人数据
    :return:
    """
    passenger = get_passenger_data(g.user.bus_session)
    if not passenger[0]:
        return jsonify({'message': passenger[1]}), 500

    return jsonify({
        'message': 'success',
        'passenger': passenger[1],
    })


@school_bus_bp.route('/ticket/get')
def get_ticket():
    bus_data = {
        'road_from': '<span class="road_from">南方学院</span>',
        'road_to': '<span class="road_to">中大南校区</span>',
        'year': '<span class="data_y">2019-10-07</span>',
        'week': '<span class="data_week">周一</span>',
        'time': '<span class="data_hm">08:00</span>',
        'bus_id': '<div class="data_bc">班次<span class="bc_classes">zbnfzd16</span></div>'
    }
    ticket = [
        {
            'ticket_id': '<p class="erwei_num">电子票号：<span>15700259145743</span></p>',
            'passenger': '<p class="erwei_num erwei_c"  style="text-align: center;text-indent:0.2rem;font-size: 0.3rem;"><span>猪猪&nbsp;&nbsp;440415<span style="color: #ef6100">20000815</span>9981</span></p>',
            'seat': '<p class="erwei_num erwei_c" style="text-align: center;text-indent:.5rem;">座位号：<span style="font-size:.3rem;color:orange;">11</span><span style="color: #cccbc8"> （按号就坐）</span></p>',
            'take_station': '上车点：南方学院'
        },
        {
            'ticket_id': '<p class="erwei_num">电子票号：<span>15700259145743</span></p>',
            'passenger': '<p class="erwei_num erwei_c"  style="text-align: center;text-indent:0.2rem;font-size: 0.3rem;"><span>猪猪&nbsp;&nbsp;440415<span style="color: #ef6100">20000815</span>9981</span></p>',
            'seat': '<p class="erwei_num erwei_c" style="text-align: center;text-indent:.5rem;">座位号：<span style="font-size:.3rem;color:orange;">11</span><span style="color: #cccbc8"> （按号就坐）</span></p>',
            'take_station': '上车点：南方学院'
        }
    ]
    javascript = """
    <script>
    var swiper = new Swiper('.swiper-container', {
        pagination: '.swiper-pagination',
        slidesPerView: 'auto',
        centeredSlides: true,
        paginationClickable: true,
        spaceBetween: 10
    });
    var parent;
    /*function doTests(p){
        parent = p;
        createTests(newTest);
    }*/
    // doTests(document.getElementById("erwei"));
    //newTest("423514348754");
                if(2){
                console.dir(2);
               // $('.bg_stocks').css('display','block');
                if(2 ==1){
                   //alert(11);
                    html = '<div class="bg_stocks" style="display: block; "><span class="stoc">已检票</span></div>';
                }else if(2 ==2){
                    // alert(22);
                    html = '<div class="bg_stocks" style="display: block; "><span class="stoc">已作废</span></div>';
                }
                $('.erwei:eq(0)').append(html);
                //console.dir(($('.erwei :eq(0)'));
                $('.erwei:eq(0)').css('display','block');
            }else{
                console.dir(2);
                parent = $('.erwei:eq(0)')[0];
                newTest(15700259687957);
            }

                if(2){
                console.dir(2);
               // $('.bg_stocks').css('display','block');
                if(2 ==1){
                   //alert(11);
                    html = '<div class="bg_stocks" style="display: block; "><span class="stoc">已检票</span></div>';
                }else if(2 ==2){
                    // alert(22);
                    html = '<div class="bg_stocks" style="display: block; "><span class="stoc">已作废</span></div>';
                }
                $('.erwei:eq(1)').append(html);
                //console.dir(($('.erwei :eq(1)'));
                $('.erwei:eq(1)').css('display','block');
            }else{
                console.dir(2);
                parent = $('.erwei:eq(1)')[0];
                newTest(15700259684675);
            }

        function newTest(text, options){
        //parent = $('#erwei')[0];
        var testbox = document.createElement("div");
        testbox.className = "testbox";
        var format = (typeof options !== "undefined" && options.format) || "auto";
        testbox.innerHTML = '<img class="barcode"/>';
        try{
            JsBarcode(testbox.querySelector('.barcode'), text, options);
        }
        catch(e){
            testbox.className = "errorbox";
            testbox.onclick = function(){
                throw e;
            }
        }
        parent.appendChild(testbox);
    }
    /*function createTests(newTest){
        newTest("423514348754");
    }*/
</script>
    """
    return render_template('html/bus_ticket.html', bus_data=bus_data, ticket=ticket, javascript=javascript)
