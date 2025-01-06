
let userinfo = {
    username: '{{userinfo.username}}',
    login_id: '{{userinfo.login_id}}',
    group_code: '{{userinfo.group_code}}',
    read_flag: '{{userinfo.can_read}}',
    write_flag: '{{userinfo.can_write}}',
    ip_address: '{{userinfo.ip_address}}',
};

let gui = {
    gui_code: '{{gui.gui_code}}',
    template_key: '{{gui.template_key}}',
    action: '{{gui.action}}',
    system_topic: '{{gui.system_topic}}',
    path_name: '{{gui.path_name}}',
};

let gparam = '{{ gparam }}';

function params_to_json(param_str) {
    let str2 = param_str.replace(/&#x27;/gi, "").replace('{', '').replace('}', '').replace(/ /gi, '');
    let list1 = str2.split(',');
    let pararms = [];
    let param_list = [];

    list1.forEach(function (el, i) {
        pararms.push(el.split(':'));
    });

    pararms.forEach(function (el, i) {
        param_list[el[0]] = el[1];
    });
    return param_list;
}
gparam = params_to_json(gparam);

userinfo.can_read = function () {
    let result = false;
    if (userinfo.read_flag == 'True') {
        result = true;
    }
    return result;
};

userinfo.can_write = function () {
    let result = false;
    if (userinfo.write_flag == 'True') {
        result = true;
    }
    return result;
};
