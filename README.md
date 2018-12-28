# thingsboard-gateway-python

##项目结构
    thingsboard 为一个mqtt server
    thingsboard-Gateway 为一个mqtt client 与thingsboard 绑定
    另起一个mqtt server（localhost mqtt server）
    esl-gateway 与 localhost mqtt server 绑定，扫描附近的esl设备publish到localhost mqtt server
    
##项目功能
        本脚本创建两个mqtt client，一个以thingsboard-gateway的名义授权绑定thingsboard
    另一个与localhost mqtt server绑定。
        subscribe esl-gateway publish 到 localhost mqtt server的附近esl设备信息。
        解析到新的esl设备信息，保存到设备数组，并publish新的设备到thingsboard创建连接。
        解析到esl设备的属性，遥测信息，publish到thingsboard更新状态。
        
        subscribe thingsboard 下发的rpc command 解析并发送response到thingsboard
        根据rpc command 的参数，发送请求到smart price tag 服务端获取json数据，
        获取到json数据后publish到esl-gateway，esl-gateway会根据json数据中的esl设备mac地址去更新esl设备图片
        