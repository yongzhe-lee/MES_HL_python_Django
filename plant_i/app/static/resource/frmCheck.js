/********************************************************************
 *
 * Form 관련 스크립트 함수 모음
 *
 *******************************************************************/
// 폼 검증 함수
function checkForm(f) {
	var rtnV = true;

	f = $(f);
	f.find("input, select, textarea").each(function () {
        const fObj = $(this);                                                   // 폼 요소
        const fOId = fObj.attr("id");                                           // 폼 ID 이름
        const fTyp = toUpperCase(fObj.attr("type")) || fObj.prop("tagName");    // 폼 요소 Type
        const fVal = $.trim(fObj.val());                                        // 폼 요소 Value
        const fMsg = fObj.data("msg");                                          // 경고 메시지 속성
        const fNum = fObj.data("chknum");                                       // 숫자만 입력 속성
        const fMax = fObj.data("maxlength");                                    // 최대 길이 지정
        const fKMax = fObj.data("maxlengthk");                                  // 최대 길이 지정(한글)
        const fMin = fObj.data("minlength");                                    // 최소 길이 지정                                 
        const fMxN = fObj.data("maxnum");                                       // 최대값 지정
        const fMnN = fObj.data("minnum");                                       // 최소값 지정
        const fMal = fObj.data("chkmail");                                      // 메일 FORMAT
        const fLng = fObj.data("chklen");                                       // 고정 길이 체크
        const fNumEng = fObj.data("chknumeng");                                 // 영문, 숫자만 체크
        const fUrl = fObj.data("chkurl");                                       // url (http, https) 체크
        const fSUrl = fObj.data("chkssl");                                      // ssl url(https) 체크

        // 체크해야 하는 필수 폼인지 확인
        let chkBool = fMsg !== undefined || getLen(fVal) > 0;

        // 입력 필드 유효성 검사
        if (chkBool && fMsg !== undefined) {
            if ((fTyp === "INPUT" || fTyp === "TEXT" || fTyp === "HIDDEN" || fTyp === "TEXTAREA" || fTyp === "PASSWORD") && fVal.replace(/ /gi, "") === "") {
                alertFocus('유효성 검사', fMsg + " 입력해 주세요", fObj);
                rtnV = false;
                return false;
            }

            if (fTyp === 'SELECT' && fVal === "") {
                alertFocus('유효성 검사', fMsg + " 입력해 주세요", fObj);
                rtnV = false;
                return false;
            }

            if (fTyp === "FILE" && fVal === "") {
                alertFocus('유효성 검사', fMsg + " 입력해 주세요", fObj);
                rtnV = false;
                return false;
            }

            if (fTyp === "RADIO" && checkChecked(fOId, "radio") === false) {
                alertFocus('유효성 검사', fMsg + " 선택해 주세요", fObj);
                rtnV = false;
                return false;
            }

            if (fTyp === "CHECKBOX" && checkChecked(fOId, "checkbox") === false) {
                alertFocus('유효성 검사', fMsg + " 선택해 주세요", fObj);
                rtnV = false;
                return false;
            }
        }

        // 숫자만 입력 체크
        if (chkBool && fNum !== undefined && !isNumeric(fVal)) {
            alertFocus('유효성 검사', "숫자로만 입력해 주세요", fObj);
            rtnV = false;
            return false;
        }

        // 최대 길이 체크
        if (chkBool && fMax !== undefined && fMax < getLen(fVal)) {
            alertFocus('유효성 검사', "입력된 글자수가 " + fMax + "자보다 작아야합니다.", fObj);
            rtnV = false;
            return false;
        }

        // 한글 최대 길이 체크
        if (chkBool && fKMax !== undefined && fKMax < getLen(fVal)) {
            alertFocus('유효성 검사', "입력된 글자수가 " + fKMax + "자보다 작아야합니다.\n(영문 " + fKMax + "자, 한글 " + Math.floor(fKMax / 2) + "자 까지 가능합니다.)", fObj);
            rtnV = false;
            return false;
        }

        // 최소 길이 체크
        if (chkBool && fMin !== undefined && fMin > getLen(fVal)) {
            alertFocus('유효성 검사',"입력된 글자수가 " + (fMin - 1) + "자보다 커야합니다.", fObj);
            rtnV = false;
            fObj.focus();
            return false;
        }

        // 고정 길이 체크
        if (chkBool && fLng !== undefined && fLng != getLen(fVal)) {
            alertFocus('유효성 검사',"" + fLng + "자리로 입력해주세요.", fObj);
            rtnV = false;
            fObj.focus();
            return false;
        }

        // 최대값 체크
        if (chkBool && fMxN !== undefined && parseInt(fMxN) < parseInt(fVal)) {
            alertFocus('유효성 검사',"입력된 숫자는 " + fMxN + "보다 작아야합니다.", fObj);
            rtnV = false;
            return false;
        }

        // 최소값 체크
        if (chkBool && fMnN !== undefined && parseInt(fMnN) > parseInt(fVal)) {
            alertFocus('유효성 검사',"입력된 숫자는 " + fMnN + "보다 커야합니다.", fObj);
            rtnV = false;
            return false;
        }

        // 이메일 형식 체크
        if (chkBool && fMal !== undefined && !checkEmail(fVal) && fVal !== "") {
            alertFocus('유효성 검사',"이메일 주소가 올바르지 않습니다", fObj);
            rtnV = false;
            return false;
        }

        // 영문, 숫자만 체크
        if (chkBool && fNumEng !== undefined && !checkNumEng(fVal) && fVal !== "") {
            alertFocus('유효성 검사',fNumEng + " 영문, 숫자를 조합해서 입력해주세요.", fObj);
            rtnV = false;
            return false;
        }

        // URL 형식 체크
        if (chkBool && fUrl !== undefined && !checkUrl(fVal) && fVal !== "") {
            alertFocus('유효성 검사',"URL이 올바르지 않습니다.", fObj);
            rtnV = false;
            return false;
        }

        // SSL URL 형식 체크
        if (chkBool && fSUrl !== undefined && !checkSSLUrl(fVal) && fVal !== "") {
            alertFocus('유효성 검사',"SSL URL이 올바르지 않습니다.", fObj);
            rtnV = false;
            return false;
        }
    });

	return rtnV;
}

// 폼에 해당하는 컨트롤들의 기본값 쉽게 셋팅해 주기
/*function initForm(f) {
	var ival;	// 각 요소의 default value 값 즉! 초기화하고자 하는값(일치형)
	var ivalin;	// 각 요소의 default value 값 즉! 초기화하고자 하는값(포함형)
	var fTyp;	// form 요소의 타입(select, radio, checkbox...)

	$("#" + f + " input, #" + f + " select").each(function () {
		fObj = $(this);
		fOId = $(this).attr("id");
		fTyp = toUpperCase(fObj.attr("type"));
		ival = $(this).attr("ival");
		ivalin = $(this).attr("ivalin");

		// 이상한 케이스 발견 사용자 쪽에서 select 타입 인식 불가
		if (fTyp == "") fTyp = "SELECT-ONE";

		if (ival != undefined && fTyp == "SELECT-ONE") {
			for (var i = 0; i < $("#" + fOId + " option").length; i++) {
				if (ival == $("#" + fOId + " option:eq(" + i + ")").val()) {
					fObj.val(ival);
				}
			}
		}
		if (ival != undefined && (fTyp == "RADIO" || fTyp == "CHECKBOX")) {
			if (ival == fObj.val()) {
				fObj.attr("checked", "checked");
			}
		}
		if (ivalin != undefined && (fTyp == "RADIO" || fTyp == "CHECKBOX")) {
			if (ivalin.indexOf(fObj.val()) != -1) {
				fObj.attr("checked", "checked");
			}
		}
	});
}*/

function isNumeric(value) {
    return !isNaN(value) && !isNaN(parseFloat(value));
}
function checkChecked(objid, objType) {
	return !!$(`input:${objType}[id='${objid}']:checked`).val();
}

function checkEmail(str) {
	const reg = /^((\w|[\-\.])+)@((\w|[\-\.])+)\.([A-Za-z]+)$/;
	return reg.test(str);
}

function getLen(str) {
	let totalLength = 0;
	for (let char of str) {
		totalLength += (char.charCodeAt(0) > 0x7F) ? 2 : 1;
	}
	return totalLength;
}

function toUpperCase(str) {
	return str ? str.toUpperCase() : "";
}

function checkEng(str) {
	return /[a-zA-Z]/.test(str);
}

function checkNumEng(str) {
	return /^[a-zA-Z0-9]+$/.test(str);
}

function checkNumEng2(str) {
	return /^[a-z]+[a-z0-9]{4,20}$/g.test(str);
}

function checkNumEngChar(str) {
	const reg1 = /[a-zA-Z0-9_]/;
	const reg2 = /[^a-zA-Z0-9_]/;
	return reg1.test(str) && reg2.test(str);
}

function checkNumEngChar2(str) {
	const regExp4 = /^(?=.*[a-zA-Z])(?=.*[^a-zA-Z0-9])(?=.*[0-9]).{10,}$/;
	return regExp4.test(str);
}

function checkKorChar(str) {
	const reg1 = /^[\uac00-\ud7a3]*$/;
	return reg1.test(str);
}

function checkNumEngKorChar(str) {
	const reg1 = /[`~!@#$%^*()\-_=+\\\|\[\]{};:\'",.<>\/?]/gi;
	return reg1.test(str);
}

function checkSearchChar(str) {
	const reg1 = /^[\uac00-\ud7a3]*$/;
	const reg2 = /^[a-zA-Z0-9]+$/;
	return reg1.test(str) || reg2.test(str);
}

function isDefindeChars(inputValue, chars) {
	for (let char of inputValue) {
		if (chars.indexOf(char) === -1) return false;
	}
	return true;
}

function checkUrl(str) {
	const regex = /^(http:\/\/|https:\/\/)/;
	return regex.test(str);
}

function checkSSLUrl(str) {
	const regex = /^https:\/\//;
	return regex.test(str);
}

// 폼체크 알럿
function alertFocus(title, msg, obj) {
    var alertDialog = Alert.alert(title, msg);
    alertDialog.bind('close', function () {
        setTimeout(function () {
            obj.focus();
        }, 100);
    });
    return alertDialog;
}