// 시스템 공통으로 사용되는 function script (default layout 사용)
// 공통콤보, validatin 등

'use strict';

let Alert = {
    alert: function (title, content, okText = '확인', focusTarget = null) {
        if (!title) {
            title = i18n.getCommonText('정보');
        }

        const $alert = $("<div></div>").kendoAlert({
            title: title,
            content: content,
            messages: {
                okText: okText,
            },
            open: function () {
                // 25.03.25 kendo css 커스텀을 위한 wrapper class(alert-container) 추가
                const $wrapper = $(this.element).closest(".k-dialog-wrapper");
                if ($wrapper.length) {
                    $wrapper.addClass("alert-container");

                    // 상태 클래스 추가 (error 포함 시)
                    if (title.toLowerCase().includes('error') || title.includes('오류')) {
                        $wrapper.addClass("error");
                    }
                }
            },
            close: function () {               
                // 확인 버튼 클릭 시 focusTarget이 input이면 focus
                if (focusTarget) {                   
                    setTimeout(function() {
                        let $el = $(focusTarget);
                        if ($el.length && $el.is('input')) {
                            $el[0].focus();
                        }
                    }, 200);
                }
            }
        });

        // open()으로 alert 띄우기
        return $alert.data("kendoAlert").open();
    },

    confirm: function (title, content, okFunc, cancelFunc) {
        // title이 빈 값일 때 기본값 설정
        if (!title) {
            title = i18n.getCommonText('확인');
        }

        return $("<div></div>").kendoConfirm({
            title: title,
            content: content,
            messages: {
                okText: i18n.getCommonText('확인'),
                cancel: i18n.getCommonText('취소'),
            },
            open: function () {
                // 25.03.25 김하늘 kendo css 커스텀을 위한 wrapper class(alert-container) 추가
                const $wrapper = $(this.element).closest(".k-dialog-wrapper");
                if ($wrapper.length) {
                    $wrapper.addClass("alert-container");

                    // 상태 클래스 추가 (error 포함 시)
                    if (title.toLowerCase().includes('error') || title.includes('오류')) {
                        $wrapper.addClass("error");
                    }
                } 
            }
        }).data("kendoConfirm").open().result
            .done(function () {
                okFunc();
            })
            .fail(function () {
                if (typeof cancelFunc !== 'undefined') {
                    cancelFunc();
                }
            });
    },
}

let Notify = (function () {
    // kendoNotification 인스턴스를 한 번만 생성
    let notification = $("<span></span>").kendoNotification({
        position: {
            pinned: true,
            top: null,
            left: null,
            bottom: 20,
            right: 40
        },
        stacking: "up", // 알림이 아래로 쌓이도록 설정
        hideOnClick: true,
        autoHideAfter: 3000 // 자동으로 3초 후 사라짐
    }).data("kendoNotification");

    return {
        success: function (message) {
            notification.show(message, "success");
        },
        error: function (message) {
            notification.show(message, "error");
        },
        info: function (message) {
            notification.show(message, "info");
        },
        warning: function (message) {
            notification.show(message, "warning");
        }
    };
})();


// 사용안함
let BookMarkUtil = {
    findMainTabs: function () {
        // not used
        // 메인화면의 nthTabs 찾기. 부모에서 찾아야 함. 이게 의미가 있나?
        let $nthTabs = $('#main-tabs').nthTabs();
        return $nthTabs
    },

    addMenuBookmark: function () {
        //즐겨찾기 리스트에 추가
        $.getJSON('/api/system/bookmark', function (_data) {
            var litagbook = '';
            for (var i = 0; i < _data.length; i++) {
                litagbook += '<li><a href="#" data-manual="' + _data[i].ismanual + '" data-objid="' + _data[i].code + '" menuurl="' + _data[i].url + '"><i class="star_icon"></i>' + i18n.getMenuText(_data[i].name) + '</a></li>';
            }
            $('#bookmark-menu').html(litagbook);

            $('#bookmark-menu a').on('click', function (e) {
                let mainTabs = parent.nthTabs;

                var val = $(this).text();
                var menuurl = $(this).attr('menuurl');
                var objid = $(this).attr('data-objid');
                var _manual = $(this).attr('data-manual');
                if (mainTabs.isExistsTab('#' + objid)) {
                    mainTabs.toggleTab('#' + objid);
                } else {
                    mainTabs.addTab({
                        id: objid,
                        title: val,
                        url: menuurl,
                        active: true,
                        allowClose: true,
                        ismanual: _manual
                    });
                    // menu_log insert 
                }
                /* 탭 추가 생성시 북마크아이콘 추가*/
                if (!$("[href*=#" + objid + "]").find("i").hasClass("fa-star")) {
                    $("[href*=#" + objid + "]").prepend("<i class='fas fa-star bookmark'></i>");
                    $(".nav-tabs .fa-star").off('click').on('click', function (e) {
                        $(this).toggleClass("bookmark");
                        BookMarkUtil.fnBookMarkSave($(this).parent('a').prop('hash').replace('#', ''), $(this).hasClass('bookmark'));
                    });
                }
            });
        }).fail(function (e) {
            Notify.error('즐겨찾기 메뉴 생성에 실패하였습니다.');
        });
    },

    fnBookMarkSave: function (_objId, _isbookmark) {
        let csrf = $('[name=csrfmiddlewaretoken]').val();
        let param_data = {
            'menucode': _objId,
            isbookmark: _isbookmark,
            'csrfmiddlewaretoken': csrf
        };
        $.post('/api/system/bookmark?action=save', param_data, function (data) {
            if (_isbookmark) {
                $('.documents a[data-objid="' + _objId + '"]').attr('data-bookmark', 'true');
            } else {
                $('.documents a[data-objid="' + _objId + '"]').attr('data-bookmark', 'false');
            }
            BookMarkUtil.addMenuBookmark();
        }).fail(function (e) {
            console.log('fnBookMarkSave error', e.message);
        });
    },

    fnCheckTabBookMark: function () {
        if (!$("[href*=#" + objid + "]").find("i").hasClass("fa-star")) {
            $("[href*=#" + objid + "]").prepend("<i class='fas fa-star" + (_bookmark == 'true' ? ' bookmark' : '') + "'></i>");
            $(".nav-tabs .fa-star").off('click').on('click', function (e) {
                $(this).toggleClass("bookmark");
                BookMarkUtil.fnBookMarkSave($(this).parent('a').prop('hash').replace('#', ''), $(this).hasClass('bookmark'));
            });
        }
    },
};

var CommonUtil = {
    bindEnterKey: function (selector, callback) {
        $(selector).keypress(function (e) {
            if (e.keyCode === 13) {
                callback(e);
            }
        });
    },
    onkeyupEnter: function (form) {
        if (window.event.keyCode == 13) {
            $(form).submit();
        }
    },
    onchangeCombobox: function (value, callback) {
        if (value != '') {
            $('#searchForm').submit();
            if (typeof callback == 'function') {
                callback();
            }
        }
    },
    getTimeStamp: function () {
        var d = new Date();
        var s =
            d.getFullYear() + '-' +
            d.getMonth() + 1 + '-' +
            d.getDate() + '_' +
            d.getHours() +
            d.getMinutes() +
            d.getSeconds();
        return s;
    },
    getYYYYMMDDHHmm: function() {
        var today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0'); // 월은 0부터 시작하므로 +1
        const day = String(today.getDate()).padStart(2, '0');
        const hours = String(today.getHours()).padStart(2, '0');
        const minutes = String(today.getMinutes()).padStart(2, '0');

        const dateDt = `${year}-${month}-${day} ${hours}:${minutes}`;
        return dateDt
    },
    getCalculatedDate: function (baseDate, adjustment, inputFormat = "YYYY-MM-DD", outputFormat = "YYYY-MM-DD 00:00") {
        // 기본 날짜 설정
        const today = new Date();
        let date = baseDate ? new Date(baseDate) : today;
    
        // `adjustment` 파싱
        const match = adjustment.match(/([+-]?\d+)([dmy])/); // e.g., -1d, +2y
        if (!match) {
            throw new Error("Invalid adjustment format. Use format like '-1d', '+2m', '+2y'.");
        }
    
        const value = parseInt(match[1], 10); // 숫자
        const unit = match[2]; // 단위: d(일), m(월), y(년)
    
        // 날짜 조정
        switch (unit) {
            case "d": // 일 단위
                date.setDate(date.getDate() + value);
                break;
            case "m": // 월 단위
                date.setMonth(date.getMonth() + value);
                break;
            case "y": // 연 단위
                date.setFullYear(date.getFullYear() + value);
                break;
            default:
                throw new Error("Unsupported unit. Use 'd' for days, 'm' for months, or 'y' for years.");
        }
    
        // 날짜 포맷팅
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
    
        // 출력 포맷에 따른 처리
        switch (outputFormat) {
            case "YYYY-MM-DD":
                return `${year}-${month}-${day}`;
            case "YYYY-MM-DD 00:00":
                    return `${year}-${month}-${day} 00:00`;
            case "YYYY-MM-DD HH:mm":
                return `${year}-${month}-${day} ${hours}:${minutes}`;
            case "MM/DD/YYYY":
                return `${month}/${day}/${year}`;
            default:
                throw new Error("Unsupported output format. Use 'YYYY-MM-DD', 'YYYY-MM-DD HH:mm', or 'MM/DD/YYYY'.");
        }
    },
    addDays: function (date, days) {
        var result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    },
    getYYMMDD: function (_diff) {
        _diff = _diff || 0;
        var d = new Date();
        d.setDate(d.getDate() + _diff);
        var m = d.getMonth() + 1;
        var day = d.getDate();
        if (m < 10) {
            m = "0" + m;
        }
        if (day < 10) {
            day = "0" + day;
        }
        var str = d.getFullYear() + '-' + m + '-' + day;

        return str.substr(2, str.length - 2);
    },
    getYYYYMMDD: function (_diff) {
        _diff = _diff || 0;
        var d = new Date();
        d.setDate(d.getDate() + _diff);
        var m = d.getMonth() + 1;
        var day = d.getDate();
        if (m < 10) {
            m = "0" + m;
        }
        if (day < 10) {
            day = "0" + day;
        }
        var str = d.getFullYear() + '-' + m + '-' + day;
        return str;
    },
    formatYYYYMMDD: function (p_date) {
        let m = p_date.getMonth() + 1;
        let day = p_date.getDate();
        if (m < 10) {
            m = "0" + m;
        }
        if (day < 10) {
            day = "0" + day;
        }
        var str = p_date.getFullYear() + '-' + m + '-' + day;
        return str;
    },
    //from to 숫자 입력값 유효성 체크(title 입력 필요)
    checkValidNumberRange: function (from, to) {
        if (Number(from.val()) > Number(to.val())) {
            let msg = from.attr("title") + ' 가 ' + to.attr("title") + ' 보다 높습니다'.
                //Alert.alert('', getMessage('valid.msg.validrange',[from.attr("title"),to.attr("title")]));
                Alert.alert('', msg);
            return false;
        }
        return true;
    },
    // 검색조건에 필수 여부 확인(title 입력 필요)
    isRequired: function (objs) {
        if (objs !== null && $.type(objs) === 'array') {
            $.each(objs, function (i) {
                if (objs[i].val() == "") {
                    Alert.alert('', objs[i].attr("title") + "을(를) 입력해 주십시오.");
                    //Alert.alert('', objs[i].attr("title")+getMessage('valid.msg.M000000041'));
                    return false;
                }
            });
        }
        return true;
    },
    CommaNumber: function (value) {
        // 수치값인 경우 3자리 기준으로 콤마를 넣어서 출력한다. 
        // 12345678.2345 -> 12,345,678.2345
        if (value == null)
            return null;
        let value2 = parseFloat(value);

        //if ( Number.isNaN(value2) ) return value;

        if (value2 == 0) return 0;

        let reg = /(^[+-]?\d+)(\d{3})/;
        let n = (value2 + '');

        while (reg.test(n)) n = n.replace(reg, '$1' + ',' + '$2');

        return n;
    },  // CommaNumber
    removeNullFromObject: function (dic) {
        // object의 value가 null 값인 경우 ''로 치환해 준다. 화면에 null로 표시되는 것을 방지하기 위해 사용.
        if (Array.isArray(dic)) {
            for (let obj of dic) {
                CommonUtil.removeNullFromObject(obj);
            }
        }
        for (const [key, value] of Object.entries(dic)) {
            if (Array.isArray(value))
                CommonUtil.removeNullFromObject(value);
            else if (value === null || value === undefined)
                dic[key] = '';
            else if (value.constructor.name === 'Object')
                CommonUtil.removeNullFromObject(value);
        }
        //return dic;
    },  // removeNullFromObject
    getParameters: function (paramName) {
        // 리턴값을 위한 변수 선언
        var returnValue;
        // 현재 URL 가져오기
        var url = location.href;
        // get 파라미터 값을 가져올 수 있는 ? 를 기점으로 slice 한 후 split 으로 나눔
        var parameters = (url.slice(url.indexOf('?') + 1, url.length)).split('&');

        // 나누어진 값의 비교를 통해 paramName 으로 요청된 데이터의 값만 return
        for (var i = 0; i < parameters.length; i++) {
            var varName = parameters[i].split('=')[0];
            if (varName.toUpperCase() == paramName.toUpperCase()) {
                returnValue = parameters[i].split('=')[1];
                return decodeURIComponent(returnValue);
            }
        }
    },
    openWindowPost: function (url, frm, options) {
        if (!options) {
            options = {};
        }

        if (!options.width) {
            options.width = 1024;
        }
        if (!options.height) {
            options.height = 768;
        }
        if (!options.layout) {
            options.layout = 'resizable=no, toolbar=no, menubar=no, location=no, status=no, scrollbars=yes';
        }
        if (!options.winname) {
            options.winname = '__window__' + Math.floor((Math.random() * 1000000) + 1);
        }

        var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
        var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;
        var screenWidth = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
        var screenHeight = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;
        if (!options.left) {
            options.left = (screenWidth / 2) - (options.width / 2) + dualScreenLeft;
        }
        if (!options.top) {
            options.top = (screenHeight / 2) - (options.height / 2);
        }

        if (options.params) {
            var params = '';
            $.each(options.params, function (name, value) {
                if (params != '') {
                    params += '&';
                }
                params += name + '=' + value;

            });
            url += params ? '?' + params : '';
        }
        window.open('', options.winname, 'top=' + options.top + ', left=' + options.left + ', width=' + options.width + ', height=' + options.height + ', ' + options.layout);
        $('#' + frm).attr('action', url);
        $('#' + frm).attr('target', options.winname);
        $('#' + frm).submit();
        return false;
    },
    openWindow: function (url, options) {
        if (!options) {
            options = {};
        }

        if (!options.width) {
            options.width = 1024;
        }
        if (!options.height) {
            options.height = 768;
        }
        if (!options.layout) {
            options.layout = 'resizable=no, toolbar=no, menubar=no, location=no, status=no, scrollbars=yes';
        }
        if (!options.winname) {
            options.winname = '__window__' + Math.floor((Math.random() * 1000000) + 1);
        }

        var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
        var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;
        var screenWidth = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
        var screenHeight = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;
        if (!options.left) {
            options.left = (screenWidth / 2) - (options.width / 2) + dualScreenLeft;
        }
        if (!options.top) {
            options.top = (screenHeight / 2) - (options.height / 2);
        }

        if (options.params) {
            var params = '';
            $.each(options.params, function (name, value) {
                if (params != '') {
                    params += '&';
                }
                params += name + '=' + value;

            });
            url += params ? '?' + params : '';
        }
        return window.open(url, options.winname, 'top=' + options.top + ', left=' + options.left + ', width=' + options.width + ', height=' + options.height + ', ' + options.layout);
    },
    onlyNumber: function (event) {
        // 숫자만 입력
        event = event || window.event;
        var keyID = (event.which) ? event.which : event.keyCode;
        if ((keyID >= 48 && keyID <= 57) || (keyID >= 96 && keyID <= 105) || keyID == 8 || keyID == 46 || keyID == 37 || keyID == 39)
            return;
        else
            return false;
    },
    removeChar: function (event) {
        //문자제거
        event = event || window.event;
        var keyID = (event.which) ? event.which : event.keyCode;
        if (keyID == 8 || keyID == 46 || keyID == 37 || keyID == 39)
            return;
        else
            event.target.value = event.target.value.replace(/[^0-9]/g, "");
    },
    sizeOf: function (obj) {
        if (obj !== null && obj !== undefined) {
            switch (typeof obj) {
                case 'number':
                    bytes += 8;
                    break;
                case 'string':
                    bytes += obj.length * 2;
                    break;
                case 'boolean':
                    bytes += 4;
                    break;
                case 'object':
                    var objClass = Object.prototype.toString.call(obj).slice(8, -1);
                    if (objClass === 'Object' || objClass === 'Array') {
                        for (var key in obj) {
                            if (!obj.hasOwnProperty(key)) continue;
                            CommonUtil.sizeOf(obj[key]);
                        }
                    }
                    else {
                        bytes += obj.toString().length * 2;
                    }
                    break;
            }
        }
        return bytes;
    },
    toggleFullScreen: function (element_id) {
        //let element = document.querySelector("body");
        let element = document.querySelector(element_id);
        if (!document.fullscreenElement) {
            if (element.requestFullscreen) return element.requestFullscreen()
            if (element.webkitRequestFullscreen)
                return element.webkitRequestFullscreen()
            if (element.mozRequestFullScreen) return element.mozRequestFullScreen()
            if (element.msRequestFullscreen) return element.msRequestFullscreen()
        } else {
            if (document.exitFullscreen) return document.exitFullscreen()
            if (document.webkitCancelFullscreen)
                return document.webkitCancelFullscreen()
            if (document.mozCancelFullScreen) return document.mozCancelFullScreen()
            if (document.msExitFullscreen) return document.msExitFullscreen()
        }
    },
    convertApprLineNameHtml: function (apprLine, apprLineState) {
        let ret = [];
        if (apprLine != null && apprLine != '') {
            let arrLine = apprLine.split(' ▶ ');
            let arrLineState = apprLineState.split('||');
            $.each(arrLineState, function (index, item) {
                let html = arrLine[index];
                if (item == 'process') {
                    html = '<span style="color:#5d9cec;">' + arrLine[index] + '</span>';
                }
                ret.push(html);
            });
        }
        return ret.join(' ▶ ');
    },
    convertApprStateCss: function (stateName, state) {
        let cssName = '';
        if (state == 'process') {
            cssName = 'grid-appr-state-blue';
        } else if (state == 'write' || state == null) {
            cssName = 'grid-appr-state-yellow';
        } else if (state == 'reject') {
            cssName = 'grid-appr-state-red';
        }

        return cssName;
    },
    convertNumberFormat: function (_value) {
        if (_value === '' || _value === null || _value === undefined) {
          return '';
        } else {
          let conVertValue = _value;
      
          // 숫자인 경우에만 처리
          if (!isNaN(Number(String(conVertValue).replaceAll(' ', '')))) {
            // 기본 언어를 'KR'(한국)으로 설정
            const formatter = new Intl.NumberFormat('KR');
      
            // 통화 형식을 사용하여 쉼표 및 소수점 변환
            formatter.formatToParts(1000.1).forEach(_data => {
              if (_data.type === 'group') {
                // 쉼표 변환
                conVertValue = String(conVertValue).replaceAll(',', _data.value);
              } else if (_data.type === 'decimal') {
                // 소수점 변환
                conVertValue = String(conVertValue).replaceAll('.', _data.value);
              }
            });
          }
      
          return conVertValue;
        }
    }
};

/******************************************************************/
let FormUtil = {
    extractForm: function ($form, disabledFields = []) {
        let _this = this;
        let values = {};
        if ($form) {
            let form = $form.serializeArray();	
            form.map(val => {
                values[val.name] = val.value;
            });

            // kendoSwitch 상태 처리
            $form.find('[data-role="switch"]').each(function () {
                let switchName = $(this).attr('name');
                let switchChk = $(this).data("kendoSwitch");
                if (switchChk) {
                    values[switchName] = switchChk.check() ? 'Y' : 'N';
                }
            });
      
            // kendoDropDownTree 상태 처리
            $form.find('[data-role="dropdowntree"]').each(function () {
                let dropdowntreeName = $(this).attr('name');
                let dropdowntreeWidget = $(this).data("kendoDropDownTree");

                if (dropdowntreeWidget) {
                    values[dropdowntreeName] = dropdowntreeWidget.value();  // 선택된 값으로 설정
                }
            });

            // kendoMultiSelect 상태 처리 (여러 값 ,로 연결)
            $form.find('[data-role="multiselect"]').each(function () {
                let multiName = $(this).attr('name');
                let multiWidget = $(this).data("kendoMultiSelect");
                if (multiWidget) {
                    let selected = multiWidget.value();
                    values[multiName] = Array.isArray(selected) ? selected.join(',') : selected;
                }
            });

        }
        disabledFields.map(val => {
            values[val] = $form.find('#' + val).val();
        });

        return values;
    },
    // serialize시에 disabled값도 포함하여 serialize 리턴
    disabledSerialize: function (_useForm) {
        var disableds = _useForm.find(':input:disabled').removeAttr('disabled');
        var params = _useForm.serialize();
        disableds.attr('disabled', 'disabled');
        return params;
    },

    // 데이터를 Form내부 Control 에 바인딩 (name으로 매칭)
    BindDataForm: function (_resultSet, $form) {
        jQuery.each(_resultSet, function (key, value) {
            // 빈스트링으로 오는 값은 반드시 null 값으로 치환한다. 또는 json 에서 null 로 넘겨준다
            // 치환하지 않고 빈스트링값('') 으로 처리하면 input[value=] 이렇게 되어 오류 발생함.
            if (key === '') value = null;
            if (value === '') value = null;       
            
            var $frmCtl = $form.find('[name=' + key + ']');

            if ($frmCtl.length == 0)
                return true;
            let object = $frmCtl[0];
            var tagName = object === undefined ? '' : object.tagName.toUpperCase();
            var tagClassName = object === undefined ? '' : object.className.toUpperCase();
            let type_name = object.type;

            //console.log('form control', $frmCtl);
            if ($frmCtl.attr("data-role") === "switch") { // kendoSwitch 처리
                let switchChk = $frmCtl.data("kendoSwitch");
                if (switchChk) {
                    switchChk.check(value === "Y"); // "Y"면 check true, "N"이면 false
                }
            } else if (tagName == 'SELECT') {
                if ($frmCtl.is(':disabled')) { $frmCtl.removeAttr('disabled'); }
                $frmCtl.val(value);

                if ($frmCtl.attr("data-role") === "dropdownlist") {
                    let kendoDropDown = $frmCtl.data("kendoDropDownList");
                    if (kendoDropDown) {
                        // 데이터가 로드되었는지 확인
                        if (kendoDropDown.dataSource.data().length === 0) {
                            // 데이터가 아직 로드되지 않은 경우, dataBound 이벤트 후에 값 설정
                            kendoDropDown.one("dataBound", function () {
                                console.log('kendoDropDownList_xxx1');
                                kendoDropDown.value(value);
                            });
                        } else {
                            // 데이터가 로드된 경우, 바로 값 설정
                            kendoDropDown.value(value);
                        }
                    }
                } else if ($frmCtl.attr("data-role") === "combobox") {
                    let kendoCombo = $frmCtl.data("kendoComboBox");
                    if (kendoCombo) {
                        if (kendoCombo.dataSource.data().length === 0) {
                            kendoCombo.one("dataBound", function() {
                                kendoCombo.value(value);
                            });
                        } else {
                            kendoCombo.value(value);
                        }
                    }
                } else if ($frmCtl.attr("data-role") === "dropdowntree") {
                    let kendoDropDownTree = $frmCtl.data("kendoDropDownTree");
                    if (kendoDropDownTree) {
                        kendoDropDownTree.value(value);
                    }
                } else {
                    // 일반 SELECT 요소인 경우에만 val() 사용
                    $frmCtl.val(value);
                }

            } else if (tagName == 'INPUT' || tagName == 'TEXTAREA') {
                if ($frmCtl.is(':disabled')) { $frmCtl.removeAttr('disabled'); }
                if (type_name == 'checkbox') {                    
                    let checkValue = $frmCtl.val();
                    if (checkValue != undefined)
                        $frmCtl.prop('checked', value == checkValue);
                    else
                        $frmCtl.prop('checked', value);                   
                } else if (type_name == 'radio') {
                    $frmCtl.removeAttr('checked');
                    var $radioCtl = $('input:radio[name=' + key + ']:input[value=' + value + ']');
                    $radioCtl.prop('checked', true);
                    $radioCtl.attr('checked', true);
                } else {
                    if ($.isNumeric(value) || value === null) {
                        $frmCtl.val(value);
                    } else {
                        $frmCtl.val(value.replace('&amp;', '&'));
                    }
                }
            } else if (tagName == 'SPAN') {
                if (tagClassName == 'DATE') {
                    var ddspan = new Date(value);
                    $frmCtl.text(ddspan.toLocaleString());
                } else {
                    $frmCtl.text(value);
                }
            }
        });
    },

    resetForm: function ($form) {
        $form[0].reset();
        
        // hidden 필드 리셋
        $form.find('input[type="hidden"]').each(function () {
            $(this).val('');
        });

        // kendo 위젯 리셋
        $form.find('[data-role]').each(function () {
            //let widget = $(this).data("kendo" + $(this).data("role").charAt(0).toUpperCase() + $(this).data("role").slice(1));
            /*Kendo UI 위젯은 생성 시 data - role 속성이 DOM에 자동으로 붙지 않습니다.
            → $(this).data("role") 값이 undefined라서 kendoDropDownTree를 못 찾는 경우입니다.*/
            let widget = kendo.widgetInstance($(this), kendo.ui);

            if (widget) {                
                if (widget instanceof kendo.ui.DropDownList || widget instanceof kendo.ui.ComboBox || widget instanceof kendo.ui.DropDownTree) {          
                    widget.value(''); // 기본값으로 리셋
                } else if (widget instanceof kendo.ui.NumericTextBox) {
                    widget.value(''); // 기본값으로 리셋
                } else if (widget instanceof kendo.ui.DatePicker) {
                    widget.value(''); // 기본값으로 리셋
                } else if (widget instanceof kendo.ui.Switch) {
                    widget.check(false); // 체크 상태 리셋 (false)
                } else if (widget instanceof kendo.ui.TextBox || widget instanceof kendo.ui.TextArea) {
                    widget.value(''); // 텍스트 값 리셋
                }
            } else {
                // kendo 위젯이 아닌 경우
                $(this).val('');
            }
        });
    },

    // Form 비활성화 처리
    disableForm: function ($form) {
        if ($form && $form.length > 0) {
            // 모든 input, select, textarea, button 비활성화
            $form.find('input, select, textarea, button').each(function () {
                if (!$(this).is(':disabled')) {
                    $(this).attr('disabled', 'disabled');
                }
            });
    
            // Kendo UI 위젯 비활성화
            $form.find('[data-role]').each(function () {
                let role = $(this).data('role');
                let widget = null;
                
                // Kendo 위젯 타입에 따라 명확히 위젯 접근 방식 지정
                switch (role) {
                    case 'textbox':
                        widget = $(this).data('kendoTextBox');
                        break;
                    case 'dropdownlist':
                        widget = $(this).data('kendoDropDownList');
                        break;
                    case 'combobox':
                        widget = $(this).data('kendoComboBox');
                        break;
                    case 'switch':
                        widget = $(this).data('kendoSwitch');
                        if (widget) {
                            widget.enable(false);  // Switch 비활성화
                            widget.check(false);   // Switch 체크 상태 리셋
                        }
                        break;
                    case 'datepicker':
                        widget = $(this).data('kendoDatePicker');
                        break;
                    case 'datetimepicker':
                        widget = $(this).data('kendoDateTimePicker');
                        break;
                    case 'timepicker':
                        widget = $(this).data('kendoTimePicker');
                        break;
                    case 'numerictextbox':
                        widget = $(this).data('kendoNumericTextBox');
                        break;
                    case 'maskedtextbox':
                        widget = $(this).data('kendoMaskedTextBox');
                        break;
                    case 'autocomplete':
                        widget = $(this).data('kendoAutoComplete');
                        break;
                    case 'multiselect':
                        widget = $(this).data('kendoMultiSelect');
                        break;
                    case 'slider':
                        widget = $(this).data('kendoSlider');
                        break;
                    case 'colorpicker':
                        widget = $(this).data('kendoColorPicker');
                        break;
                    case 'editor':
                        widget = $(this).data('kendoEditor');
                        break;
                    case 'upload':
                        widget = $(this).data('kendoUpload');
                        break;
                    default:
                        break;
                }
    
                if (widget && typeof widget.enable === 'function' && role !== 'switch') {
                    widget.enable(false);  // 모든 Kendo 위젯 비활성화
                } else {
                    $(this).val('');  // 일반 HTML 요소 값 리셋
                    $(this).attr('disabled', 'disabled');  // 일반 폼 요소 비활성화
                }
            });
        }
    },

    enableForm: function ($form) {
        if ($form && $form.length > 0) {
            // 모든 input, select, textarea, button 활성화
            $form.find('input, select, textarea, button').each(function () {
                $(this).removeAttr('disabled');  // 폼 요소 활성화
            });
    
            // Kendo UI 위젯 활성화
            $form.find('[data-role]').each(function () {
                //console.log('this', this);
                let role = $(this).data('role');
                let widget = null;

                // Kendo 위젯 타입에 따라 명확히 위젯 접근 방식 지정
                switch (role) {
                    case 'textbox':
                        widget = $(this).data('kendoTextBox');
                        break;
                    case 'dropdownlist':
                        widget = $(this).data('kendoDropDownList');
                        break;
                    case 'dropdowntree':
                        widget = $(this).data('kendoDropDownTree');
                        break;
                    case 'combobox':
                        widget = $(this).data('kendoComboBox');
                        break;
                    case 'switch':
                        widget = $(this).data('kendoSwitch');
                        let elem_id = null;
                        if (widget.element && widget.element.length > 0)
                            elem_id = widget.element[0].id;
                        //if (widget) {
                        //    widget.enable(true);  // Switch 활성화
                        //}
                        if (widget && elem_id == 'use_yn') {
                            widget.check(true);   // 사용여부는 기본값을 On으로 설정 
                        }
                        break;
                    case 'datepicker':
                        widget = $(this).data('kendoDatePicker');
                        break;
                    case 'datetimepicker':
                        widget = $(this).data('kendoDateTimePicker');
                        break;
                    case 'timepicker':
                        widget = $(this).data('kendoTimePicker');
                        break;
                    case 'numerictextbox':
                        widget = $(this).data('kendoNumericTextBox');
                        break;
                    case 'maskedtextbox':
                        widget = $(this).data('kendoMaskedTextBox');
                        break;
                    case 'autocomplete':
                        widget = $(this).data('kendoAutoComplete');
                        break;
                    case 'multiselect':
                        widget = $(this).data('kendoMultiSelect');
                        break;
                    case 'slider':
                        widget = $(this).data('kendoSlider');
                        break;
                    case 'colorpicker':
                        widget = $(this).data('kendoColorPicker');
                        break;
                    case 'editor':
                        widget = $(this).data('kendoEditor');
                        break;
                    case 'upload':
                        widget = $(this).data('kendoUpload');
                        break;
                    default:
                        break;
                }

                //if (widget && typeof widget.enable === 'function' && role !== 'switch') {
                //    widget.enable(true);  // 모든 Kendo 위젯 활성화
                //} else {
                //    $(this).removeAttr('disabled');  // 일반 폼 요소 활성화
                //}
                if (widget && typeof widget.enable === 'function') {
                    widget.enable(true);  // 모든 Kendo 위젯 활성화
                } else {
                    $(this).removeAttr('disabled');  // 일반 폼 요소 활성화
                }
                // 디폴트값 지정
                if (widget && widget.element && widget.element.length > 0) { 
                    let elem_id = widget.element[0].id;
                    if (elem_id == 'use_yn' && typeof widget.check === 'function') {
                        widget.check(true);   // 사용여부는 기본값을 On으로 설정 
                    }
                }
            });
        }
    }
    
    
};

let AjaxUtil = {
    failureCallback: function (req, status, error) {
        let message = '에러가 발생했습니다.';
        console.log(status);
        try {
            message = JSON.parse(req.responseText).message;
        }
        catch (ex) {
            message = req.responseText;
            console.log(req.responseText, ex);
        }
		//Notify.error(message);
		Alert.alert('Error', message);
	},
    getSyncData: function (url, p_data, fn_failure) {
       let items = null;
        $.ajax({
            async: false,
            dataType: 'json',
            type: 'GET',
            url: url,
			data: p_data,
            success: function (res) {
                items = res;
            },
            error: function (req, staus, error) {
                console.log('getSyncData error', error, url);
                if (typeof fn_failure !== 'undefined') {
                    fn_failure(error);
                } else {
                    AjaxUtil.failureCallback(req, staus, error);
                }
            }
        });

        return items;
	},
	getAsyncData: function (url, param_data, fn_success, fn_failure) {
        $.ajax({
            async: true,
            dataType: 'json',
            type: 'GET',
            url: url,
            data: param_data,
            success: function (res) {
                fn_success(res);
            },
            error: function (req, status, error) {
                console.log('getAsyncData error', error, url);
                if (typeof fn_failure !== 'undefined') {
                    fn_failure(req, status, error);
                } else {
                    AjaxUtil.failureCallback(req, status, error);
                }
            }
        });
	},

    // POST저장시에는 성공여부를 확인하여 분기하는 루틴이 많으므로, items만 리턴할 것이 아니라 
    // 성공여부와 메시지도 리턴한다
    postSyncData: function (url, param_data, fn_failure) {
        let result = null;
		let csrf = $('[name=csrfmiddlewaretoken]').val();

		if (param_data != null && typeof param_data === 'object') {
			param_data['csrfmiddlewaretoken'] = csrf;
        }

        $.ajax({
            async: false,
            dataType: 'json',
            type: 'POST',
            url: url,
            data: param_data,
            success: function (res) {
                result = res;
            },
            failure: function (req, staus, error) {
                if (typeof fn_failure !== 'undefined') {
                    fn_failure(req, staus, error);
                } else {
                    AjaxUtil.failureCallback(req, staus, error);
                }
            }
        });
        return result;
    },
    postAsyncData: function (url, param_data, fn_success, fn_failure) {
        let result = null;

        if (param_data != null && typeof param_data === 'object') {
            if (param_data.hasOwnProperty('csrfmiddlewaretoken') == false) {
                let csrf = $('[name=csrfmiddlewaretoken]').val();
                param_data['csrfmiddlewaretoken'] = csrf;
            }
        }

        $.ajax({
            async: true,
            dataType: 'json',
            type: 'POST',
            url: url,
            data: param_data,
            success: function (res) {
                //console.log('post success res', res);
                fn_success(res);
            },
            failure: function (req, staus, error) {
                if (typeof fn_failure !== 'undefined') {
                    fn_failure(req, staus, error);
                } else {
                    
                    AjaxUtil.failureCallback(req, staus, error);
                }
            }
        });
    },
    postFileSyncData: function (url, form_data, fn_failure) {
        let result = null;

        if (form_data != null && typeof form_data === 'object') {
            let csrf = $('[name=csrfmiddlewaretoken]').val();
            form_data.append("csrfmiddlewaretoken", csrf);
        }

        $.ajax({
            async: false,
            type: 'POST',
            url: url,
            data: form_data,
            processData: false,
            contentType: false,
            success: function (res) {
                result = res;
            },
            failure: function (req, staus, error) {
                if (typeof fn_failure !== 'undefined') {
                    fn_failure(req, staus, error);
                } else {
                    AjaxUtil.failureCallback(req, staus, error);
                }
            }
        });
        return result;
    },
    postFileAsyncData: function (url, form_data, fn_success, fn_failure) {
        let result = null;

        if (form_data != null && typeof form_data === 'object') {
            let csrf = $('[name=csrfmiddlewaretoken]').val();
            form_data.append("csrfmiddlewaretoken", csrf);
        }

        $.ajax({
            async: true,
            type: 'POST',
            url: url,
            data: form_data,
            processData: false,
            contentType: false,
            success: function (res) {
                //console.log('post success res', res);
                fn_success(res);
            },
            failure: function (req, staus, error) {
                if (typeof fn_failure !== 'undefined') {
                    fn_failure(req, staus, error);
                } else {

                    AjaxUtil.failureCallback(req, staus, error);
                }
            }
        });
    },
    getSelectData: function (combo_type, cond1, cond2, cond3) {
        let data = {
            combo_type: combo_type,
        };
        if (cond1 !== undefined) {
            data.cond1 = cond1;
        }
        if (cond2 !== undefined) {
            data.cond2 = cond2;
        }
        if (cond3 !== undefined) {
            data.cond3 = cond3;
        }
        let ret = AjaxUtil.getSyncData('/api/system/combo', data);
        return ret;
    },
    getSelectDataWithNull: function (combo_type, null_option, condition1, condition2, condition3) {
        let ret = AjaxUtil.getSelectData(combo_type, condition1, condition2, condition3);
        let text = null_option;
        if (null_option == 'choose') {
            text = i18n.getCommonText('선택');//'선택하세요(Choose)';
        }
        else if (null_option == 'all') {
            text = i18n.getCommonText('전체'); //'전체(All
        }
        else {
            return ret;
        }

        let option = {
            'value': '',
            'text': text,
        };

        ret.unshift(option);

        return ret;
    },
    fillSelectOptions : function ($combo, combo_type, null_option, selected_value, condition1, condition2, condition3) {
        let rows = AjaxUtil.getSelectDataWithNull(combo_type, null_option, condition1, condition2, condition3);
        //console.log('rows fillSelectOptions', rows);
        $combo.empty();
        $.each(rows, function (index, row) {
            //let option = $('<option>',
            //    {
            //        value: row['value'],
            //        text: row['text'],
            //    });
            let option = $('<option>');
            option.val(row['value']).text(row['text']);
            //console.log('fill option row', row);    
            Object.keys(row).forEach(function (key) {
                //console.log('key', key);
                if (key != 'value' && key != 'text')
                    option.data(key, row[key]);
            });

            $combo.append(option);
        });

        if (selected_value) {
            $combo.val(selected_value).change();
        }

        return rows;
    },
    fillSelectOptionsRows: function ($combo, rows, null_option, selected_value) {
        // 원본 배열을 수정하지 않기 위해 복사본 생성
        let updatedRows = rows.slice();
    
        // 기본 옵션 추가
        let defaultText = null_option === 'choose' ? '선택' : '전체';
        if (defaultText) {
            let defaultOption = { value: '', text: defaultText };
            updatedRows.unshift(defaultOption); // 기본 옵션을 맨 앞에 추가
        }
    
        // 콤보박스 초기화 및 옵션 추가
        $combo.empty();
        $.each(updatedRows, function (index, row) {
            let option = $('<option>');
            option.val(row['value']).text(row['text']);
            $combo.append(option);
        });
    
        // 선택된 값 설정
        if (selected_value) {
            $combo.val(selected_value).change();
        }
    
        // KendoDropDownList 새로고침
        let dropdown = $combo.data("kendoDropDownList");
        if (dropdown) {
            dropdown.dataSource.data(updatedRows);
            dropdown.refresh();
        }
    
        return updatedRows;
    },


    fillSelectSyncData: function ($combo, url, param, null_option, selected_value) {
        $combo.empty();
        let rows = AjaxUtil.getSyncData(url, param);
        //console.log('fillSelectSyncData rows', rows);
        if (rows != null) {
            let text = null_option;
            if (null_option == 'choose') {
                text = '선택';//'선택하세요(Choose)';
            }
            else if (null_option == 'all') {
                text = '전체'; //'전체(All
            }
            if (text) {
                let option = {
                    'value': '',
                    'text': text,
                };

                rows.unshift(option);
            }
            
            $.each(rows, function (index, row) {
                let option = $('<option>',
                    {
                        value: row['value'],
                        text: row['text'],
                    });
                $combo.append(option);
            });

            if (selected_value) {
                $combo.val(selected_value).change();
            }
        }
    },

    downloadFile(url, filename) {
        fetch(url)
            .then(resp => resp.blob())
            .then(blob => {
                //console.log('download blob', url);
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                // the filename you want
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                //alert('your file has downloaded!'); 
                //Notify.success('다운로드 성공');
            }).catch(() => {
                console.log('download error', url);
                let message = '에러가 발생했습니다.관리자에게 문의 주세요.';
                //Notify.error(message);
                Alert.alert('Error', message);
            });

        //let url = yullin.getUrl({ api: api_url + '?' + param + '=' + val });
        //var link = document.createElement("a");
        //$(link).click(function (e) {
        //    e.preventDefault();
        //    window.location.href = url;
        //});
        //$(link).click();
        //$(link).remove();
    },

    fillDropDownOptions: function ($combo, $combo_type, null_option, selected_value, condition1, condition2, condition3) {
        let rows = AjaxUtil.getSelectDataWithNull($combo_type, null_option, condition1, condition2, condition3);
        $combo.empty();

        $combo.kendoDropDownList({
            dataTextField: "text",
            dataValueField: "value",
            dataSource: rows
        });

        let dropdownlist = $combo.data("kendoDropDownList");

        if (selected_value) {
            dropdownlist.value(selected_value);
        }

    },
    fillComboOptions: function ($combo, $combo_type, null_option, selected_value, condition1, condition2, condition3) {
        let rows = AjaxUtil.getSelectDataWithNull($combo_type, null_option, condition1, condition2, condition3);
        $combo.empty();

        $combo.kendoComboBox({
            dataTextField: "text",
            dataValueField: "value",
            filter: "contains",
            dataSource: rows
        })

        let combolist = $combo.data("kendoComboBox");

        if (selected_value) {
            combolist.value(selected_value);
        }

    },

    fillDropDownTreeOptions: function ($combo, $combo_type, null_option, con1) {
        let _url = '';
        switch ($combo_type)
        {
            case 'depart':
                _url = '/api/system/depart?action=depart_tree';
                break;
            case 'cm_location':
                _url = '/api/definition/location?action=cm_loc_tree';
                break;
            case 'cm_equip_classify':
                _url = '/api/definition/equipment?action=cm_equip_classify_tree&category=' + con1;
                break;
            default:
                break;
        }

        // 이미 DropDownTree가 있으면 destroy 후 재초기화
        if ($combo.data('kendoDropDownTree')) {
            $combo.data('kendoDropDownTree').destroy();
            $combo.show();
        }

        $combo.kendoDropDownTree({
            dataSource: {
                transport: {
                    read: {
                        url: _url,
                        type: "GET",
                        dataType: "json"
                    }
                },
                schema: {
                    data: function (response) {
                        return response.items || [];  // ✅ 'items' 안의 데이터만 반환
                    },
                    model: {
                        id: "id",
                        text: "text",
                        children: "items"  // ✅ DropDownTree가 items를 하위 항목으로 인식
                    }
                }
            },
            dataTextField: "text",
            dataValueField: "id",
            placeholder: null_option == 'select' ? i18n.getCommonText('선택') : i18n.getCommonText('전체'),
            height: 400
        });
    },

    fillMultiSelectOptions: function ($multiselect, $combo_type, null_option, selected_values, condition1, condition2, condition3) {
        let rows = AjaxUtil.getSelectDataWithNull($combo_type, null_option, condition1, condition2, condition3);
        $multiselect.empty();

        $multiselect.kendoMultiSelect({
            dataTextField: "text",
            dataValueField: "value",
            dataSource: rows,
            placeholder: null_option == 'select' ? i18n.getCommonText('선택') : i18n.getCommonText('전체'),
            filter: "contains",
            clearButton: true
        });

        let multiselect = $multiselect.data("kendoMultiSelect");

        if (selected_values && Array.isArray(selected_values) && selected_values.length > 0) {
            multiselect.value(selected_values);
        }
    },
};
// kendo 공통 모듈화
var kendoUtil = {
    /* --------------------------------------- element --------------------------------------- */
    /**
     * @param {object} $start_selector
     * @param {object} $end_selector
     * @param {string} _startValue
     * @param {string} _endValue
     */
    kenDateTimePicker: function ($start_selector, $end_selector, _startValue, _endValue) {
        var smp_date_start = $start_selector.kendoDateTimePicker({
            value: _startValue,
            change: startChange,
            format: "yyyy-MM-dd HH:mm",
            parseFormats: ["yyyy-MM-dd HH:mm"]
        }).data("kendoDateTimePicker");

        var smp_date_end = $end_selector.kendoDateTimePicker({
            value: _endValue,
            change: endChange,
            format: "yyyy-MM-dd HH:mm",
            parseFormats: ["yyyy-MM-dd HH:mm"]
        }).data("kendoDateTimePicker");

        smp_date_start.max(smp_date_end.value());
        smp_date_end.min(smp_date_start.value());

        function startChange() {
            var startDate = smp_date_start.value(),
                endDate = smp_date_end.value();

            if (startDate) {
                startDate = new Date(startDate);
                startDate.setDate(startDate.getDate());
                smp_date_end.min(startDate);
            } else if (endDate) {
                smp_date_start.max(new Date(endDate));
            } else {
                endDate = new Date();
                smp_date_start.max(endDate);
                smp_date_end.min(endDate);
            }
        }

        function endChange() {
            var endDate = smp_date_end.value(),
                startDate = smp_date_start.value();

            if (endDate) {
                endDate = new Date(endDate);
                endDate.setDate(endDate.getDate());
                smp_date_start.max(endDate);
            } else if (startDate) {
                smp_date_end.min(new Date(startDate));
            } else {
                endDate = new Date();
                smp_date_start.max(endDate);
                smp_date_end.min(endDate);
            }
        }
    },
    /**
     * 
     * @param {object} item
     * @param {string} gbn
     * @returns {string} template
     */
    createStateBar: function (item, gbn) {
        return this.generateStateBarTemplate(item, gbn, item.outOffYn, item.inOffYn);
    },

    /**
     * 
     * @param {object} item
     * @param {string} gbn
     * @returns {string} template
     */
    createStateBarIssue: function (item, gbn) {
        return this.generateStateBarTemplate(item, gbn, item.issueOffYn, item.issueOffYn);
    },

    /**
     * 
     * @param {object} item
     * @param {string} state
     * @param {string} outOff
     * @param {string} inOff
     * @returns {string} template
     */
    generateStateBarTemplate: function (item, gbn, outOffYn, inOffYn) {
        let state = gbn === 'smp_state' ? item.smp_state : item.req_state;
        let forCnt = 0;
        const barCnt = 6;
        let color = 'gray';

        state = Number(state);

        // 공장 상태 처리
        if (gbn === 'smp_state') {
            color = smpColorSetting(state, outOffYn, inOffYn);
            forCnt = smpForCntSetting(state);
        } else {
            if (state <= 20) {
                color = 'blue';
                forCnt = (state === 10) ? 1 : 2;
            } else if (state > 20) {
                color = 'green';
                if (state > 20 && state < 50) forCnt = 3;
                else if (state === 50) forCnt = 4;
                else if (state === 60) forCnt = 5;
                else if (state >= 70) forCnt = 6;
            }
        }

        // bar 색상 설정 함수
        function smpColorSetting(state, outOffYn, inOffYn) {
            let color = 'gray'; // 기본값
            if (state >= 40 && state <= 50) {
                color = outOffYn === 'Y' ? 'red' : 'orange';
            }
            if (state <= 20) {
                color = 'blue';
            } else if (state > 20 && state <= 90) {
                color = outOffYn === 'Y' ? 'red' : inOffYn === 'Y' ? 'orange' : 'green';
            }
            return color;
        }

        // bar 갯수 설정 함수
        function smpForCntSetting(state) {
            let forCnt = 0;
            if (state === 10) forCnt = 1;
            else if (state === 15 || state === 20) forCnt = 2;
            else if (state > 20 && state < 50) forCnt = 3;
            else if (state === 50) forCnt = 4;
            else if (state === 60) forCnt = 5;
            else if (state >= 70) forCnt = 6;
            return forCnt;
        }

        let template = '<div class="smp_state_wrapper">';
        for (let i = 0; i < forCnt; i++) {
            template += '<div class="smp_state_div_' + color + '"></div>';
        }

        for (let i = 0; i < barCnt - forCnt; i++) {
            template += '<div class="smp_state_div_gray"></div>';
        }
        template += '</div>';

        return template;
    },
    /* --------------------------------------- function --------------------------------------- */
    /**
     * @param {object} $selector
     * purpose: 그리드 행 수 표시
     */
    showGridRowCount: function ($selector) {
        // 그리드 요소의 바로 이전 형제 요소에서 label을 찾아옴
        var $label = $selector.prev('.card-group-btn').find('label');

        if ($label.length > 0) {
            // label에 있는 data-labelCd 값을 가져와서 필요 없는 부분 제거
            var labelCdValue = $label.attr('data-labelCd') ? $label.attr('data-labelCd').replace(/\(\d+건\)$/, '').trim() : '';

            // 25.04.15 김하늘 (treeGrid도 count할 수 있게 수정)
            var grid = $selector.data("kendoGrid") || $selector.data("kendoTreeList");
            //var grid = $selector.data("kendoGrid");
            var rowCount = grid ? grid.dataSource.total() : 0; // 그리드의 총 행 개수

            // data-labelCd 속성과 텍스트 값을 업데이트
            $label.attr('data-labelCd', labelCdValue + " (" + rowCount + "건)");
            $label.text(labelCdValue + " (" + rowCount + "건)");
        }
    },
    /**
     * @param {object} $selector
     * purpose: 단일 행 return
     */
    getGridSelectedRow: function ($selector) {
        var grid = $selector.data("kendoGrid") ? $selector.data("kendoGrid"): $selector.data("kendoTreeList") 
        if (!grid) return;
        var selected = grid.select();
        let selectedRow = grid.dataItem(selected); // 선택된 행의 데이터

        return selectedRow;
    },
    /**
     * @param {object} $selector
     * purpose: 체크된 행 return
     */
    getGridCheckedRows: function ($selector) {
        var grid = $selector.data("kendoGrid")
        if (!grid) return;
        var selected = grid.select();
        var selectedRowsArr = [];

        selected.each(function() {
            var selectedRow = grid.dataItem($(this));
            selectedRowsArr.push(selectedRow);
        });

        return selectedRowsArr;
    },
    /**
     * @param {object} $selector
     * purpose: 선택 및 체크된 행 삭제
     */
    removeGridCheckedRows: function ($selector) {
        var grid = $selector.data("kendoGrid");
        if (!grid) return;
        (grid.select().toArray()).forEach((item) => {
            grid.removeRow(item);
        });
    },
    /**
     * @param {object} $selector
     * purpose: removeRow처리된 row return
     */
    getGridRemovedRows: function ($selector) {
        var grid = $selector.data("kendoGrid");
        if (!grid) return;
        return grid.dataSource._destroyed;
    },
    /**
     * @param {object} $selector - Kendo Grid의 jQuery 선택자
     * @returns {Array} - 편집된 항목의 배열
     * purpose: 편집된 행의 데이터를 추출
     */
    getGridEditedRows: function ($selector, _initialData) {
        const grid = $selector.data("kendoGrid");
        if (!grid) return [];
        let getGridData = kendoUtil.getGridData($selector);
        // 수정된 데이터 저장용 배열
        let modifiedRows = [];
        // 초기 데이터와 현재 데이터를 비교
        getGridData.forEach((currentRow, index) => {
            const initialRow = _initialData.find(item => item.id === currentRow.id);
            if (initialRow) {
                // 비교할 필드 리스트
                const fieldsToCompare = ["char_val", "n1", "n2", "n3", "n4", "n5"];

                const modifiedFields = fieldsToCompare.filter(field => {
                    const initialValue = initialRow[field];
                    const currentValue = currentRow[field];
                    // ""와 null 값을 동일한 값으로 취급하여 비교
                    if ((initialValue === "" || initialValue === null) && (currentValue === "" || currentValue === null)) {
                        return false; // 두 값이 같으면 수정되지 않은 것으로 처리
                    }
                    return initialValue !== currentValue; // 값이 다르면 수정된 필드로 간주
                });

                if (modifiedFields.length > 0) {
                    // 수정된 행 및 필드 기록 (console debug 편의를 위해)
                    // modifiedRows.push({
                    //     id: currentRow.id,
                    //     modifiedFields: modifiedFields,
                    //     newData: currentRow,
                    //     originalData: initialRow
                    // });
                    modifiedRows.push(currentRow);

                }
            }
        }); 
        // console.log("modifiedRows", modifiedRows)
        return modifiedRows
    },
    /**
     * @param {object} $selector
     * purpose: grid data return
     */
    getGridData: function ($selector) {
        var grid = $selector.data("kendoGrid");
        if (!grid) return;
        return grid.dataSource.view();
    },
    /**
     * @param {object} $selector
     * purpose: kendo grid data > general grid data return
     */
    getJsonGridData: function ($selector, Nofilter) {
        var grid = $selector.data("kendoGrid");
        if (!grid) return;
        var gKendoData = Nofilter ? grid.dataSource.data() : grid.dataSource.view()
        const jsonGridData = gKendoData.map(item => {
            return item.toJSON ? item.toJSON() : item;  // Kendo 데이터 객체를 일반 객체로 변환
        });
        return jsonGridData
    },
    /**
     * @param {object} $selector
     * purpose: test 그룹별로 cell merge
     * param: hideCheckBox - merge된 cell 중 1번째 row만 box 표시
     */
    setCellMerge: function ($selector, hideCheckBox) {
        let previousValue = null;
        let mergeTargetCells = $selector;

        let rowspanCount = 0; // rowspan을 계산할 카운터
        let mergeStartIndex = -1; // 병합 시작 인덱스 (-1로 초기화)

        mergeTargetCells.each(function (index) {
            let currentCell = $(this); // 현재 셀
            let currentValue = currentCell.text().trim();

            if (currentValue === previousValue) {
                // 현재 셀이 이전 셀과 값이 같은 경우
                currentCell.css("display", "none"); // 현재 셀을 숨김 (셀을 숨겨야 rowspan 값을 바꿨을 때 칸이 맞음)
                rowspanCount++;
            } else {
                // 이전 값과 다른 경우, 이전 셀에 rowspan 설정
                if (previousValue !== null && rowspanCount > 0) {
                    let mergeCell = mergeTargetCells.eq(mergeStartIndex);
                    mergeCell.attr('rowspan', rowspanCount + 1);
                }
                // 초기화 및 현재 셀로 값 갱신
                previousValue = currentValue;
                rowspanCount = 0;
                mergeStartIndex = index;
            }
        });

        // 마지막 값에 대한 rowspan 설정
        if (rowspanCount > 0) {
            let mergeCell = mergeTargetCells.eq(mergeTargetCells.length - rowspanCount - 1);
            mergeCell.attr('rowspan', rowspanCount + 1); // rowspan 설정
        }
        if(hideCheckBox){
            // 병합한 cell 자식 check box 숨기기
            mergeTargetCells.each(function (index, item) {
                let $item = $(item);
                let rowspan = $item.attr("rowspan");

                const rowCount = parseInt(rowspan) || 1; // rowspan이 없으면 1로 설정
                for (let i = 1; i < rowCount; i++) { // 첫 번째 행은 건너뜀
                    let targetRow = $item.closest("tr").nextAll().eq(i - 1);
                    let targetCheckbox = targetRow.find("input[type='checkbox']");
                    targetCheckbox.hide();
                }
            });
        }
    },
    /**
     * @param {object} $selector
     * purpose: 기존 cell merge 상태 sync
     * param: 
     */
    setCellMergeWithSync : function ($primarySelector, $secondarySelector, hideCheckBox = true) {
        let previousValue = null;
        let mergeTargetCells = $primarySelector;
        let mergeSecondaryCells = $secondarySelector;
    
        let rowspanCount = 0; // rowspan을 계산할 카운터
        let mergeStartIndex = -1; // 병합 시작 인덱스 (-1로 초기화)
    
        // 첫 번째 셀 병합 기준으로 처리
        mergeTargetCells.each(function (index) {
            let currentCell = $(this); // 현재 셀
            let currentValue = currentCell.text().trim();
            let secondaryCell = mergeSecondaryCells.eq(index); // 동일한 인덱스의 두 번째 셀
    
            if (currentValue === previousValue) {
                // 현재 셀이 이전 셀과 값이 같은 경우
                currentCell.css("display", "none"); // 현재 셀을 숨김
                secondaryCell.css("display", "none"); // 두 번째 셀도 숨김
                rowspanCount++;
            } else {
                // 이전 값과 다른 경우, 이전 셀에 rowspan 설정
                if (previousValue !== null && rowspanCount > 0) {
                    let mergeCell = mergeTargetCells.eq(mergeStartIndex);
                    let secondaryMergeCell = mergeSecondaryCells.eq(mergeStartIndex);
                    mergeCell.attr('rowspan', rowspanCount + 1);
                    secondaryMergeCell.attr('rowspan', rowspanCount + 1);
                }
                // 초기화 및 현재 셀로 값 갱신
                previousValue = currentValue;
                rowspanCount = 0;
                mergeStartIndex = index;
            }
        });
    
        // 마지막 값에 대한 rowspan 설정
        if (rowspanCount > 0) {
            let mergeCell = mergeTargetCells.eq(mergeTargetCells.length - rowspanCount - 1);
            let secondaryMergeCell = mergeSecondaryCells.eq(mergeTargetCells.length - rowspanCount - 1);
            mergeCell.attr('rowspan', rowspanCount + 1);
            secondaryMergeCell.attr('rowspan', rowspanCount + 1);
        }
    
        if (hideCheckBox) {
            // 병합한 cell 자식 check box 숨기기
            mergeTargetCells.each(function (index, item) {
                let $item = $(item);
                let rowspan = $item.attr("rowspan");
    
                const rowCount = parseInt(rowspan) || 1; // rowspan이 없으면 1로 설정
                for (let i = 1; i < rowCount; i++) { // 첫 번째 행은 건너뜀
                    let targetRow = $item.closest("tr").nextAll().eq(i - 1);
                    let targetCheckbox = targetRow.find("input[type='checkbox']");
                    targetCheckbox.hide();
                }
            });
        }
    },
    
    /**
     * @param {object} $selector
     * purpose: merge된 cell의 check된 no값들을 배열로 반환한다.
     */
    getGridCellMergeCheckedRowArr: function ($selector, grid, checkedNosArr) {
        $selector.each(function (index, item) {
            let $item = $(item);
            let rowspan = $item.attr("rowspan");

            // 체크박스 찾기
            let $checkbox = $item.prev().find("input[type='checkbox']");
            let isChecked = $checkbox.prop("checked");

            // 체크박스가 체크된 경우와 체크 해제된 경우를 구분하여 처리
            if (isChecked) {
                handleCheckboxChange($item, true, rowspan);
            } else {
                handleCheckboxChange($item, false, rowspan);
            }

        });
        // console.log('checkedNosArr', checkedNosArr); // 배열 상태 출력

        // check box event -- merge한 cell 하위 check box (숨겨진 check box) 처리
        function handleCheckboxChange($item, isChecked, rowspan) {
            const rowCount = parseInt(rowspan) || 1; // rowspan이 없으면 1로 설정
            for (let i = 0; i < rowCount; i++) {
                let targetRow;
                if (i === 0) {
                    targetRow = $item.closest("tr"); // 현재 행
                } else {
                    targetRow = $item.closest("tr").nextAll().eq(i - 1); // 다음 행
                }

                let targetCheckbox = targetRow.find("input[type='checkbox']");
                targetCheckbox.prop("checked", isChecked);

                let dataItem = grid.dataItem(targetRow);
                if (dataItem) {
                    if (isChecked) {
                        if (!checkedNosArr.includes(dataItem.prpt_result_no)) {
                            checkedNosArr.push(dataItem.prpt_result_no);
                        }
                    } else {
                        const index = checkedNosArr.indexOf(dataItem.prpt_result_no);
                        if (index > -1) {
                            checkedNosArr.splice(index, 1);
                        }
                    }
                }
            }
        }
        return checkedNosArr;
    },
    // 공통 버튼 바인딩 함수
    bindButton: function (selector, icon = null, themeColor, clickHandler, enabled) {
        $(selector).kendoButton({
            icon: icon,
            themeColor: themeColor,
            click: clickHandler,
            enabled: enabled
        });
    },
    // 공통 Enter 키 바인딩 함수
    bindEnterKey: function (selector, action) {
        $(selector).kendoTextBox().keypress(function (e) {
            if (e.keyCode == 13) {
                action();
            }
        });
    },
    saveAsExcel: function(kendo_grid, file_name) {
        kendo_grid.grid.bind("excelExport", function (e) {
            let today = kendo.toString(new Date(), "yyyyMMdd_HHmmss");
            e.workbook.fileName = file_name + "_" + today + ".xlsx";
        });
        kendo_grid.grid.saveAsExcel();
    }
};
// 공통 팝업
var popupComn = {
    openPopup: function (_url, _options) {
        let _popupData = {};
        _popupData.param = _options.param ? _options.param : null; // 부모창 param 데이터 매칭

        // 브라우저 너비의 80%를 팝업 너비로 설정
        let windowWidth = window.innerWidth * 0.8;
        var popup = $("<div></div>").kendoWindow({
            width: _options.width || windowWidth + "px",  // 가변적인 너비 설정
            height: _options.height || "400px",
            title: _options.title || "팝업",
            actions: ["Close"],
            content: _url,
            iframe: true,
            resizable: false,
            open: function () {
                var iframe = this.wrapper.find("iframe");

                // ✅ 팝업 생성 즉시 스타일 적용하여 기본 스타일 덮어쓰기
                this.wrapper.find(".k-window-titlebar")
                    .css({
                        "background-color": "#34495e",
                        "color": "#ffffff",
                        "border-top-left-radius": "5px",
                        "border-top-right-radius": "5px"
                    });

                this.wrapper.css({
                    "border": "1px solid #2c3e50", // ✅ 테두리 추가
                    "border-radius": "5px",
                    "overflow": "hidden", // 테두리 둥글게 유지
                    "box-shadow": "none",
                    "-webkit-box-shadow": "none",
                    "-moz-box-shadow": "none"
                });

                // ✅ iframe이 깜빡거리지 않도록 숨김 처리
                iframe.css("display", "none");

                iframe.on("load", function () {
                    var contentWindow = iframe[0].contentWindow;
                    $(contentWindow.document.body).css("background-color", "#ffffff");  // iframe 흰색 배경
                    contentWindow.popupData = {
                        param: _options.param,
                        close: (result) => { 
                            popup.result = result;
                            popup.close(result);
                        }
                    };

                    // ✅ 스타일 적용 후 iframe 표시
                    setTimeout(() => {
                        $(contentWindow.document.body).css("visibility", "visible");
                        iframe.css("display", "block");
                    }, 1); // 약간의 지연을 주어 깜빡임 방지

                    // open 콜백 함수가 존재하면 호출
                    if (typeof _options.openCallback === "function") {
                        _options.openCallback(this);  
                    }
                }.bind(this))
            },
            close: function (e) {
                // close 콜백 함수가 존재하면 호출
                if (typeof _options.closeCallback === "function") {
                    // _options.closeCallback(this, arguments[0], this.callback);
                    _options.closeCallback(e.sender.result || null);
                }
                popup.destroy(); // 팝업 객체 삭제
            }
        }).data("kendoWindow");

        popup.center().open();
    },
    openTempPopup: function ($popup_selector, _options) {
        // 브라우저 너비의 80%를 팝업 너비로 설정
        let windowWidth = window.innerWidth * 0.8;

        $popup_selector.kendoWindow({
            width: _options.width || windowWidth + "px",  // 가변적인 너비 설정
            height: _options.height || "450px",
            title: _options.title || "팝업",
            visible: false,
			modal: true, // 모달 팝업으로 설정
            actions: ["Close"],
            open: function () {
                // open 콜백 함수가 존재하면 호출
                if (typeof _options.openCallback === "function") {
                    _options.openCallback(this, $popup_selector);  // this, $popup_selector는 좀 더 유연한 조작을 위해
                }
            },
            close: function () {
                // close 콜백 함수가 존재하면 호출
                if (typeof _options.closeCallback === "function") {
                    _options.closeCallback(this, $popup_selector);
                }
            }
        });
        $popup_selector.data("kendoWindow").center().open();
    },
    openSmpPopup: function (_options, _state) {
        let _popupData = {};
        _popupData.param = _options.param ? _options.param : null; // 부모창 param 데이터 매칭

        // 브라우저 너비의 80%를 팝업 너비로 설정
        let windowWidth = window.innerWidth * 0.8;

        var smpPopup = $("<div></div>").kendoWindow({
            width: _options.width || windowWidth + "px", 
            height: _options.height || "620px",
            title: _options.title || _state === 'edit' ? '샘플수정' : '샘플정보',
            actions: ["Close"],
            content: '/page/popup/popup_smp',
            iframe: true,
            resizable: false,
            open: function () {
                // 팝업이 열린 후, iframe의 내용이 로드된 후 바인딩 처리
                var iframe = this.wrapper.find("iframe");
                iframe.on("load", function () {
                    var contentWindow = iframe[0].contentWindow;
                    $(contentWindow.document.body).css("background-color", "#ffffff");  // iframe 흰색 배경
                    _popupData.popState = _state;
                    _popupData.parentPopup = smpPopup; // 팝업 객체 전달
                    contentWindow.popupData = _popupData;
                    var $reqForm = $(contentWindow.document).find('#reqPopupForm');
                    var $smpForm = $(contentWindow.document).find('#smpPopupForm');
                    FormUtil.BindDataForm(_options.param, $reqForm);
                    FormUtil.BindDataForm(_options.param, $smpForm);
                });
            },
            close: function () {
                // close 콜백 함수가 존재하면 호출
                if (typeof _options.closeCallback === "function") {
                    _options.closeCallback(this, smpPopup);
                }
            }
        }).data("kendoWindow");

        smpPopup.center().open();
    },
    openSmpHistPopup: function (_options) {
        let _popupData = {};
        _popupData.param = _options.param ? _options.param : null; // 부모창 param 데이터 매칭

        // 브라우저 너비의 80%를 팝업 너비로 설정
        let windowWidth = window.innerWidth * 0.8;

        var smpHistPopup = $("<div></div>").kendoWindow({
            width: _options.width || windowWidth + "px",
            height: _options.height || "620px",
            title: _options.title || '이력조회',
            actions: ["Close"],
            content: '/page/popup/popup_smp_hist',
            iframe: true,
            resizable: false,
            open: function () {
                var iframe = this.wrapper.find("iframe");
                iframe.on("load", function () {
                    var contentWindow = iframe[0].contentWindow;
                    $(contentWindow.document.body).css("background-color", "#ffffff");  // iframe 흰색 배경
                    contentWindow.popupData = _popupData;
                    var $smpHistForm = $(contentWindow.document).find('#histPopupForm');
                    FormUtil.BindDataForm(_options.param, $smpHistForm);
                });
            }
        }).data("kendoWindow");
        smpHistPopup.center().open();
    },
};
// 업무별 공통으로 사용되는 function script (default layout 사용)
// 버튼, TAB 권한, 대시보드 function 호출, QA 상세 호출, 녹취청취 호출등

// 버튼별 권한 처리
var authDisableBtn = function (data) {
    // servlet(modelandview에서 리턴된 권한버튼,탭 데이터로 show/hide 처리)
    //console.log(data)
    // 화면별 권한에 따른 버튼 활성화 처리(show, hide)
    var btnRoleList = data.replace('[', '').replace(']', '').replace(/ /g, '').split(',');
    // [중요]권한제어할 button에는 btn-role-group 클래스명이 항상 포함되어야 함.
    $('.btn-role-group').each(function () {
        var _this = this;
        $(_this).addClass('btndisplaynone');
        $.each(btnRoleList, function () {
            var btntxt = this;
            if (_this.id == btntxt) {
                $(_this).removeClass('btndisplaynone');
            } else {
                if (btntxt.substr(btntxt.length - 1, btntxt.length) == '*') {
                    if (btntxt.substr(0, btntxt.length - 1) == _this.id.substr(0, btntxt.length - 1)) {
                        $(_this).show();
                        $(_this).removeClass('btndisplaynone');
                    }
                }
            }
        });
        $('.btndisplaynone').remove();
    });
};

// TAB별 권한처리
var authDisableTab = function (data) {
    // 화면별 권한에 따른 TAB(탭) 활성화 처리
    var tabRoleList = data.replace('[', '').replace(']', '').replace(/ /g, '').split(',');
    // [중요]권한제어할 TAP의 a태그에는 tab-role-group 클래스명이 항상 포함되어야 함.
    // tab li태그 하위의 a태그의 id로 권한 관리가 됨 - <li><a href="#tabs_detcd_tab" id="tabs_detcd" class="tab-role-group">
    // tab 화면을 삭제하기 위해 <div id="tabs_detcd_tab" class="tab-pane">처럼 tab화면 div의 ID를 'tab메뉴 a태그 id' + '_tab' 을 붙여야 함.
    $('.tab-role-group').each(function () {
        var _this = this;
        if (jQuery.inArray(_this.id, tabRoleList) < 0) {
            $('#' + _this.id).closest("li").remove();
            $('.' + _this.id + '_tab').remove();
        }
    });
    $('.tab-role-group').each(function () {
        $('#' + this.id).closest("li").addClass('active role');
        $('#' + this.id).trigger('click');
        $('.' + this.id + '_tab').addClass('active');
        return false;
    });
};

// 다국어 처리
var i18n = {
    modal: null,
    mask: null,
    commonModal: null,
    commonMask : null,
    dicMonth: {
        'ko-KR': ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
        'en-US': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    },
    dicDays: {
        'ko-KR': ['일', '월', '화', '수', '목', '금', '토'],
        'en-US': ['Sun', 'Mon', 'Thu', 'Wed', 'Thu', 'Fri', 'Sat'],
    },
    url: '/api/common/labels',
    storageKeys: ['lang_code', 'kr_common_common', 'en_common_common'],
    DEFAULT_LOCALE: 'ko-KR',
    commonResource: {},
    menuResource: {},
    guiResource: {},
    resetData: function () {
        let lang_cd = i18n.getLanguageCode();
        sessionStorage.clear();
        sessionStorage.setItem('lang_code', lang_cd);
    },
    initialize: function () {
        let lang_cd = i18n.getLanguageCode();
        i18n.initializeCommonData(lang_cd);
        i18n.initializeGUIData(lang_cd);
    },
    initializeMenuData: function (lang_cd) {
        let storageKey = lang_cd + '_common_menu';
        let menuStorageData = sessionStorage.getItem(storageKey);
        let loadMenuData = function (result) {
            if (result.length > 0) {
                sessionStorage.setItem(storageKey, JSON.stringify(result));
                i18n.menuResource = {};
                $.each(result, function (idx, item) {
                    i18n.menuResource[item.label_code] = { 'text': item.text, 'desc': item.descr };
                });
            }
            else {
                sessionStorage.setItem(storageKey, null);
            }
        };
        if (menuStorageData == null || menuStorageData == 'null') {
            let data = {
                lang_code: lang_cd,
                gui_code: 'common',
                template_key: 'menu',
                action: 'read'
            };
            let result = AjaxUtil.getSyncData(i18n.url, data);
            loadMenuData(result);
        } else {
            let result = JSON.parse(menuStorageData);
            loadMenuData(result);
        }
    },
    initializeCommonData: function (lang_cd) {
        let storageKey = lang_cd + '_common_common';
        let commonStorageData = sessionStorage.getItem(storageKey);
        let loadCommonData = function (result) {
            if (result.length > 0) {
                sessionStorage.setItem(storageKey, JSON.stringify(result));
                i18n.commonResource = {};
                $.each(result, function (idx, item) {
                    i18n.commonResource[item.label_code] = { 'text': item.text, 'desc': item.descr };
                });
            } else {
                sessionStorage.setItem(storageKey, null);
            }
            i18n.applyCommonLabel();
        };
        if (commonStorageData == null || commonStorageData == 'null') {
            let data = {
                lang_code: lang_cd,
                gui_code: 'common',
                template_key: 'common',
                action: 'read'
            };
            let fnsuccess = function (result) {
                loadCommonData(result);
            };
            AjaxUtil.getAsyncData(i18n.url, data, fnsuccess);
        }
        else {
            let result = JSON.parse(commonStorageData);
            loadCommonData(result);
        }
    },
    initializeGUIData: function (lang_cd) {
        if (gui.gui_code == '') {
            return;
        }
        let storageKey = lang_cd + '_' + gui.gui_code + '_' + gui.template_key;
        let guiStorageData = sessionStorage.getItem(storageKey);
        let loadGUIData = function (result) {
            if (result.length > 0) {
                sessionStorage.setItem(storageKey, JSON.stringify(result));
                i18n.guiResource = {};
                $.each(result, function (idx, item) {
                    i18n.guiResource[item.label_code] = { 'text': item.text, 'desc': item.descr };
                });
            } else {
                sessionStorage.setItem(storageKey, null);
            }
            i18n.applyGUILabel();
        };
        if (guiStorageData == null || guiStorageData == 'null') {
            let data = {
                gui_code: gui.gui_code,
                template_key: gui.template_key,
                lang_code: lang_cd,
                action: 'read'
            };
            let fnsuccess = function (result) {
                loadGUIData(result);
            };
            AjaxUtil.getAsyncData(i18n.url, data, fnsuccess);
        }
        else {
            let result = JSON.parse(guiStorageData);
            loadGUIData(result);
        }
    },
    getLanguageCode: function () {
        let lang_cd = sessionStorage.getItem('lang_code');
        if (lang_cd == null || lang_cd == 'null') {
            lang_cd = i18n.DEFAULT_LOCALE;
            sessionStorage.setItem('lang_code', lang_cd);
        }
        return lang_cd;
    },
    getMenuText: function (code, args) {
        let result = code;
        let exist = i18n.menuResource.hasOwnProperty(code);
        if (exist) {
            result = i18n.menuResource[code].text;
            if (args !== null && $.type(args) === 'array') {
                $.each(args, function (_idx, _val) {
                    result = result.replace('{' + _idx + '}', _val);
                });
            }
        } else {
            //console.log('getGUIText 라벨코드없음', i18n.guiResource);
        }
        return result;
    },
    getGUIText: function (code, args) {
        let result = code;
        let exist = i18n.guiResource.hasOwnProperty(code);
        if (exist) {
            result = i18n.guiResource[code].text;
            if (args !== null && $.type(args) === 'array') {
                $.each(args, function (_idx, _val) {
                    result = result.replace('{' + _idx + '}', _val);
                });
            }
        } else {
            //console.log('getGUIText 라벨코드없음', i18n.guiResource);
        }

        return result;
    },
    getGUITextDefault: function (code, args, defaultText) {
        let result = defaultText;
        if (i18n.guiResource.hasOwnProperty(code)) {
            result = i18n.guiResource[code].text;
            if (args !== null && $.type(args) === 'array') {
                $.each(args, function (_idx, _val) {
                    result = result.replace('{' + _idx + '}', _val);
                });
            }
        }
        return result;
    },
    getCommonText: function (code, args) {
        let result = code;
        let exist = i18n.commonResource.hasOwnProperty(code);
        if (exist) {
            result = i18n.commonResource[code].text;
            if (args !== null && $.type(args) === 'array') {
                $.each(args, function (_idx, _val) {
                    result = result.replace('{' + _idx + '}', _val);
                });
            }
        } else {
            //console.log('getCommonText 라벨코드없음', i18n.guiResource);
        }

        return result;
    },
    applyLabel: function () {
        i18n.applyCommonLabel();
        if (gui.gui_code != '') {
            i18n.applyGUILabel();
        }
    },   
    applyGUILabel: function () {
        let $labels = $('[data-labelCd]');
        $labels.each(function () {
            var $this = $(this);
            let labelcd = $this.data('labelcd');
            let lbltext = i18n.getGUIText(labelcd);

            $this.text(lbltext);
            $this.attr('placeholder', lbltext);
        });
        
        if (userinfo.group_code == 'admin') {
            $labels.unbind('contextmenu').bind('contextmenu', 'th', function (e) {
                let labelcd = $(this).data('labelcd');
                let lang_code = i18n.getLanguageCode();
                i18n.modal = $("<div></div>").kendoWindow({
                    width: "350px",
                    height: "430px",
                    title: "label setting",
                    actions: ["Close"],
                    content: '/page/popup/label?' + 'lang_code=' + lang_code + '&label_code=' + labelcd + '&gui_code=' + gui.gui_code + '&template_key=' + gui.template_key,
                    iframe: true,
                    resizable: false
                }).data("kendoWindow");
                
                i18n.modal.center().open();
                return false;
            });
        }
    },
    applyCommonLabel: function () {
        let $labels = $('[data-commonCd]');
        $labels.each(function () {
            var $this = $(this);
            let labelcd = $this.data('commoncd');
            let lbltext = i18n.getCommonText(labelcd);
            $this.text(lbltext);
            $this.attr('placeholder', lbltext);
        });
        if (userinfo.group_code == 'admin') {
            $labels.unbind('contextmenu').bind('contextmenu', 'th', function (e) {
                let labelcd = $(this).data('commoncd');
                let lang_code = i18n.getLanguageCode();
                let paramData = {
                    lang_code: lang_code,
                    label_code: labelcd,
                    gui_code: 'common',
                    template_key: 'common',
                    //callback: 'i18n.applyCommonLabel'
                };
                
                i18n.modal = $("<div></div>").kendoWindow({
                    width: "350px",
                    height: "430px",
                    title: "label setting",
                    actions: ["Close"],
                    content: '/page/popup/label?' + 'lang_code=' + lang_code + '&label_code=' + labelcd + '&gui_code=common&template_key=common',
                    iframe: true,
                    resizable: false
                }).data("kendoWindow");

                i18n.modal.center().open();
                return false;
            });
        }
    },
    applyContentLabel: function ($popupContent) {
        let $labels = $popupContent.find('[data-labelCd]');
        $labels.each(function () {
            var $this = $(this);
            let labelcd = $this.data('labelcd');
            let lbltext = i18n.getGUIText(labelcd);

            $this.text(lbltext);
            $this.attr('placeholder', lbltext);
        });

        if (userinfo.group_code == 'admin') {
            $labels.unbind('contextmenu').bind('contextmenu', 'th', function (e) {
                let labelcd = $(this).data('labelcd');
                let lang_code = i18n.getLanguageCode();
                    
                i18n.modal = $("<div></div>").kendoWindow({
                    width: "350px",
                    height: "430px",
                    title: "label setting",
                    actions: ["Close"],
                    content: '/page/popup/label?' + 'lang_code=' + lang_code + '&label_code=' + labelcd + '&gui_code=' + gui.gui_code + '&template_key=' + gui.template_key,
                    iframe: true,
                    resizable: false
                }).data("kendoWindow");

                i18n.modal.center().open();
                return false;
            });
        }


        $labels = $('[data-commonCd]');
        $labels.each(function () {
            var $this = $(this);
            let labelcd = $this.data('commoncd');
            let lbltext = i18n.getCommonText(labelcd);
            $this.text(lbltext);
            $this.attr('placeholder', lbltext);
        });
        if (userinfo.group_code == 'admin') {
            $labels.unbind('contextmenu').bind('contextmenu', 'th', function (e) {
                let labelcd = $(this).data('commoncd');
                let lang_code = i18n.getLanguageCode();
                let paramData = {
                    lang_code: lang_code,
                    label_code: labelcd,
                    gui_code: 'common',
                    template_key: 'common',
                    //callback: 'i18n.applyCommonLabel'
                };

                i18n.modal = $("<div></div>").kendoWindow({
                    width: "350px",
                    height: "430px",
                    title: "label setting",
                    actions: ["Close"],
                    content: '/page/popup/label?' + 'lang_code=' + lang_code + '&label_code=' + labelcd + '&gui_code=common&template_key=common',
                    iframe: true,
                    resizable: false
                }).data("kendoWindow");

                i18n.modal.center().open();
                return false;
            });
        }


    },
    getMonthArrayText: function () {
        let langcd = i18n.getLanguageCode();
        if (i18n.dicMonth.hasOwnProperty(langcd)) {
            return i18n.dicMonth[langcd];
        } else {
            return i18n.dicMonth[i18n.DEFAULT_LOCALE];
        }
    },
    getDayArrayText: function () {
        let langcd = i18n.getLanguageCode();
        if (i18n.dicDays.hasOwnProperty(langcd)) {       
            return i18n.dicDays[langcd];
        } else {
            return i18n.dicDays[i18n.DEFAULT_LOCALE];
        }
    },
};

//권한처리
let yullinAuth = {
    removeWriteButton: function ($content) {
        let $items;
        if ($content)
            $items = $content.find('.y_write_auth');
        else
            $items = $('.y_write_auth');
        $items.each(function () {
            if (!userinfo.can_write()) 
                $(this).remove();
        });
    },
};

let DateUtil = {
    //
    //  Kendo DatePicker의 날짜 범위를 서버 파라미터로 변환
    //  @param {string} startDatePickerId - 시작일 DatePicker ID
    //  @param {string} endDatePickerId - 종료일 DatePicker ID  
    //  @param {string} dateType - 날짜 타입 ('month' 또는 'year')
    //  @returns {Object} 서버로 전송할 날짜 파라미터 객체
    // 
    // dateType(월, 년)별 날짜 범위를 YYYYMMDD 형식의 파라미터로 변환
    convertDateRangeToParam: function(startDatePickerId, endDatePickerId, dateType) {
        let startDate = $(startDatePickerId).data("kendoDatePicker").value();
        let endDate = $(endDatePickerId).data("kendoDatePicker").value();
        let serverDateType = dateType === 'month' ? 'MON' : 'YEAR';
        
        let result = {
            dateType: serverDateType,
            startDt: '',
            endDt: ''
        };
        
        if (serverDateType == 'MON') {
            let startYear = startDate.getFullYear();
            let startMonth = startDate.getMonth();
            let endYear = endDate.getFullYear();
            let endMonth = endDate.getMonth();
            
            let startDateObj = new Date(startYear, startMonth, 1);
            let endDateObj = new Date(endYear, endMonth + 1, 0);
            
            result.startDt = startDateObj.getFullYear().toString() + 
                           String(startDateObj.getMonth() + 1).padStart(2, '0') + 
                           String(startDateObj.getDate()).padStart(2, '0');
            result.endDt = endDateObj.getFullYear().toString() + 
                         String(endDateObj.getMonth() + 1).padStart(2, '0') + 
                         String(endDateObj.getDate()).padStart(2, '0');
        } else if (serverDateType == 'YEAR') {
            let startYear = startDate.getFullYear();
            let endYear = endDate.getFullYear();
            
            let startDateObj = new Date(startYear, 0, 1);
            let endDateObj = new Date(endYear, 11, 31);
            
            result.startDt = startDateObj.getFullYear().toString() + 
                           String(startDateObj.getMonth() + 1).padStart(2, '0') + 
                           String(startDateObj.getDate()).padStart(2, '0');
            result.endDt = endDateObj.getFullYear().toString() + 
                         String(endDateObj.getMonth() + 1).padStart(2, '0') + 
                         String(endDateObj.getDate()).padStart(2, '0');
        }
        
        return result;
    }
};

// 시간(hh24:mi)형식 validation
let DataValidation = { timeCheck: null, validateTime: null };

DataValidation.timeCheck = function (hours, minutes) {
    let i = 0;

    if (hours == "" || isNaN(hours) || parseInt(hours) > 23) {
        i++;
    } else if (parseInt(hours) == 0) {
        hours = "00";
    } else if (hours < 10 && hours.length < 2) {
        hours = "0" + hours;
    }

    if (minutes == "" || isNaN(minutes) || parseInt(minutes) > 59) {
        i++;
    } else if (parseInt(minutes) == 0) {
        minutes = "00";
    } else if (minutes < 10 && minutes.length < 2) {
        minutes = "0" + minutes;
    }

    if (i == 0) {
        return hours + ":" + minutes;
    } else {
            /*alert*/("Invalid Time Format.");
        return "";
    }
}

DataValidation.validateTime = function (obj) {
    /*
         _this.$addModal.find('#start_time').blur(function (event) {
                DataValidation.validateTime(event.target);
          });
     */
    let timeValue = obj.value;
    let sHours;
    let sMinutes;

    if (timeValue == "") {
            /*alert*/("Invalid Time format.");
        obj.value = "";
        return false;
    }
    else {
        if (timeValue.indexOf(":") > 0) {
            sHours = timeValue.split(':')[0];
            sMinutes = timeValue.split(':')[1];
            obj.value = DataValidation.timeCheck(sHours, sMinutes);
        }
        else {
            if (timeValue.length >= 4) {
                sHours = timeValue.substring(0, 2);
                sMinutes = timeValue.substring(2, 4);
                obj.value = DataValidation.timeCheck(sHours, sMinutes);
            }
            else if (timeValue.length == 3) {
                sHours = timeValue.substring(0, 2);
                sMinutes = timeValue.substring(2, 3);
                if (parseInt(sHours) > 23) {
                    sHours = timeValue.substring(0, 1);
                    sMinutes = timeValue.substring(1, 3);
                }
                obj.value = DataValidation.timeCheck(sHours, sMinutes);
            }
            else if (timeValue.length <= 2) {
                sHours = timeValue.substring(0, 2);
                sMinutes = '00';
                if (parseInt(sHours) > 23) {
                    sHours = timeValue.substring(0, 1);
                    sMinutes = timeValue.substring(1, 3);
                }
                obj.value = DataValidation.timeCheck(sHours, sMinutes);
            }
        }
        return true;
    }
}

////////////////////////////////////////////////////////////////////////////////
$(document).ready(function () { 

    //다국어 설정
    if (userinfo.login_id != '') {
        i18n.initialize();
    }

});

// kendo 커스텀 이벤트 추가
(function($) {
    $.fn.dbltouch = function(callback) {
        return this.each(function() {

            $(this).on("dblclick touchend", function(e) {
                // 더블 터치 처리
                if (e.type === 'touchend') {
                    let currentTime = new Date().getTime();
                    let tapLength = currentTime - $(this).data('lastTap') || 0;
                    $(this).data('lastTap', currentTime);

                    if (tapLength < 300 && tapLength > 0) { // 300ms 이내의 터치라면 더블 터치로 간주
                        callback.call(this, e);
                    }
                }
                // 더블 클릭 처리
                else if (e.type === 'dblclick') {
                    callback.call(this, e);
                }
            });
        });
    };
    $.fn.longpress = function(callback) {
        return this.each(function() {
            let pressTimer;
            let longPressDuration = 500; // 500ms 이상을 롱 프레스로 간주

            $(this).on("dblclick", function(e) {
                // 더블 클릭 처리 (PC)
                callback.call(this, e);
            });

            // 롱 프레스 처리 (모바일)
            $(this).on("touchstart", function(e) {
                pressTimer = setTimeout(() => {
                    callback.call(this, e);
                }, longPressDuration);
            }).on("touchend touchmove touchcancel", function() {
                clearTimeout(pressTimer); // 터치가 끝나거나 움직이면 롱 프레스 취소
            });
        });
    };
})(jQuery);

// 모달 관련 상수 정의
const MODAL_DEFAULTS = {
    WIDTH: '70%',
    HEIGHT: '70%'
};

/**
 * 자식 모달창의 크기와 위치를 부모 모달창 기준으로 설정하는 함수
 * @param {string} childModalSelector - 자식 모달창의 선택자 (예: '#modalWindow')
 * @param {Object} options - 모달 설정 옵션
 * @param {string} options.width - 모달창의 너비 (기본값: MODAL_DEFAULTS.WIDTH)
 * @param {string} options.height - 모달창의 높이 (기본값: MODAL_DEFAULTS.HEIGHT)
 * @param {number} options.zIndex - z-index 값 (기본값: 부모 z-index + 1)
 */
function setModalPosition(childModalSelector, options = { width: '70%', height: '70%' }) {
    const parentModal = $('.modal:visible').not(childModalSelector);
    if (!parentModal.length) return;

    const parentRect = parentModal[0].getBoundingClientRect();
    const childModal = $(childModalSelector);
    
    // 기본 옵션값 설정
    const defaultOptions = {
        width: options.width,
        height: options.height,
        zIndex: parseInt(parentModal.css('z-index')) + 1
    };
    
    const settings = { ...defaultOptions, ...options };

    // 모달과 모달 컨텐츠의 크기를 설정
    childModal.css({
        'width': settings.width,
        'height': settings.height,
        'max-height': settings.height
    });

    // 모달 컨텐츠의 크기도 설정
    childModal.find('.modal-content').css({
        'height': '100%',
        'max-height': '100%'
    });

    // 모달 바디의 크기 설정 (헤더와 푸터 고려)
    const modalHeader = childModal.find('.modal-header').outerHeight() || 0;
    const modalFooter = childModal.find('.modal-footer').outerHeight() || 0;
    childModal.find('.modal-body').css({
        'height': `calc(100% - ${modalHeader + modalFooter}px)`,
        'max-height': `calc(100% - ${modalHeader + modalFooter}px)`,
        'overflow-y': 'auto'
    });

    // 자식 모달의 실제 크기를 가져옴
    const childWidth = childModal.outerWidth();
    const childHeight = childModal.outerHeight();

    // 부모 모달의 중앙 좌표 계산
    const parentCenterX = parentRect.left + (parentRect.width / 2);
    const parentCenterY = parentRect.top + (parentRect.height / 2);

    // 자식 모달의 최종 위치 계산 (중앙 정렬)
    const childLeft = parentCenterX - (childWidth / 2);
    const childTop = parentCenterY - (childHeight / 2);

    // 위치 및 스타일 적용
    childModal.css({
        'position': 'fixed',
        'top': childTop,
        'left': childLeft,
        'z-index': settings.zIndex
    });
}

//JSON 표준 형식
//특히 key / value 중 'Y', 'N'처럼 Boolean으로 처리할 수 있는 값은 true / false로 자동 변환
function convertToJsonStandard(obj) {
    const converted = {};

    for (const [key, value] of Object.entries(obj)) {
        if (value === 'Y') {
            converted[key] = true;
        } else if (value === 'N') {
            converted[key] = false;
        } else if (!isNaN(value) && value.trim() !== '') {
            // 숫자 문자열 → 숫자
            converted[key] = Number(value);
        } else {
            converted[key] = value;
        }
    }

    return converted;
}
function convertToYN(obj) {
    const converted = {};

    for (const [key, value] of Object.entries(obj)) {
        if (value === true) {
            converted[key] = 'Y';
        } else if (value === false) {
            converted[key] = 'N';
        } else {
            converted[key] = value; // 숫자나 문자열은 그대로 유지
        }
    }

    return converted;
}

