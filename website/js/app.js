$(function(){
    const ZK_MONITOR_DATA_API_URL = "http://localhost:8001";

    let SERVER_SELECTED = "";
    let DATE_SELECTED = getDateBefore(0, "-")

    function draw(_data, _type, _el_id){
        let _parent = $("#"+_el_id).parent();
        $("#"+_el_id).attr("width", _parent.width())
        let data = {
            "labels": _data.labels.slice(),
            "datasets": []
        }
        let _today = {
            name: "今日数据",
            color : "#a6d854",
            pointColor : "#95A5A6",
            pointBorderColor : "#fff",
            data: []
        }
        let _first = true
        _data["keys"].forEach(function(_key){
            let _value = _data["all_data"][_key]?_data["all_data"][_key][_type]:0;
            if(_first) {
                _value += 1;
                _first = false
            }
            _today['data'].push(_value);
        });
        data["datasets"].push(_today)
        let line = new JChart.Line(data, {
           id: _el_id,
        });
        line.draw();
    }
    function drawReceive(_data){
        draw(_data, "receive", "receive_data")
    }

    function drawSend(_data){
        draw(_data, "send", "send_data")
    }

    function drawMaxLatency(_data){
        draw(_data, "max", "max_latency")
    }

    function drawAvgLatency(_data){
        draw(_data, "avg", "avg_latency")
    }

    function drawOpenFile(_data){
        draw(_data,"open_file", "open_file")
    }

    function drawNodeCount(_data){
        draw(_data, "znode", "z_node")
    }

    function drawCanvas(_data){
        if(_data && _data['all_data']&&Object.keys(_data['all_data']).length>0){
            drawSend(_data)
            drawReceive(_data)
            drawMaxLatency(_data)
            drawAvgLatency(_data)
            drawOpenFile(_data)
            drawNodeCount(_data)
        }
    }

    function getServerData(){
        J.showMask();
        $.ajax({
            url: ZK_MONITOR_DATA_API_URL+"/data/"+SERVER_SELECTED+"/"+DATE_SELECTED,
            type: "GET",
            dataType: "json",
            success: function(data){
                console.log(data.data)
                drawCanvas(data.data)
            },
            error: function(data){
                J.showToast("获取服务数据失败.")
            },
            complete: function(){
                J.hideMask()
            }
        })
    }

    function selectedDate(date=DATE_SELECTED){
        DATE_SELECTED = date
        $("#date_selected").text(DATE_SELECTED);
        getServerData();
    }

    // 获取日期
    function getDate(_date){
        let _now = _date;
        if(!_now) _now = new Date();
        if(_now.getDate()<10){
            return "0"+_now.getDate();
        }else{
            return ""+_now.getDate();
        }
    }

    //获取月份
    function getMonth(_date){
        let _now = _date;
        if(!_now) _now = new Date();

        if((_now.getMonth()+1)<10){
            return "0"+(_now.getMonth()+1);
        }else{
            return ""+(_now.getMonth()+1);
        }
    }

    //获取多少天之前的日期
    function getDateBefore(_count, _split){
        let _d = "";
        if(_split) _d = _split;
        let _delay = 0;
        if(_count && typeof(_count)==='number'){
            _delay = _count;
        }

        let _now = new Date();
        _now.setTime(_now.getTime() - 24*60*60*1000*_delay);

        return _now.getFullYear()+_d+getMonth(_now)+_d+getDate(_now);
    }

    Jingle.launch({});

    $("#date_pickup_button").tap(function(){
        J.popup({
            html: "<div id='popup_calendar'></div>",
            pos: "center",
            backgroundOpacity : 0.4,
            showCloseBtn : false,
            onShow : function(){
                new J.Calendar('#popup_calendar',{
                    date : new Date(DATE_SELECTED),
                    onSelect:function(date){
                        J.closePopup();
                        selectedDate(date)
                    }
                });
            }
        })
    })

    function getServerList(){
        J.showMask();
        $.ajax({
            type: "GET",
            dataType: "json",
            url: ZK_MONITOR_DATA_API_URL+"/server_list",
            success: function(data){
                if(data.data && data.data.length<=0){
                    J.showToast("No Servers.", "toast top", 2000);
                }else{
                    SERVER_SELECTED = data.data[0]
                    selectedDate()
                }
            },
            error: function(data){
                console.log("error:",data)
                J.showToast("获取服务器信息失败。")
            },
            complete: function(){
                J.hideMask()
            }
        })
    }

    getServerList()
})