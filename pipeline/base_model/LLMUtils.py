from openai import OpenAI
from bs4 import BeautifulSoup
import re

client = OpenAI(
    # base_url="https://blankxyz-exqauoou6xw1.gear-c1.openbayes.net/v1/", 
    base_url="http://172.17.141.17:11431/v1/", 
    api_key="sk-xxxxxxxxxxxxxxxxxxxx"
)

guided_json_format = {
    "type": "object",
    "properties": {
        "start": {
            "type": "integer",
            },
        "end": {
            "type": "integer",
        },

    },
    "required": ["start", "end"]
}

html_content = """
<html xmlns="//www.w3.org/1999/xhtml"><head>

<meta http-equiv="Content-Type" content="text/html; charset=gb2312">
<meta name="filetype" content="0">   
<meta name="publishedtype" content="1">   
<meta name="pagetype" content="2">   
<meta name="catalogs" content="32000000000000000">
<meta name="Keywords" content="黑龙江省委政法委,黑龙江政法网,平安龙江网">
<meta name="Description" content="黑龙江省委政法委,黑龙江政法网,平安龙江网">
<title>平安龙江-东北网</title>
<meta name="keywords" content="">
<meta name="description" content="">

<style type="text/css">

* {
	padding: 0;
	margin: 0;
}
body {
	color: #000000;
	font-size:12px;
	line-height:120%;
	font-family:Arial, Helvetica, sans-serif;
	background:#FFFFFF;
	width:969px;
	margin:0 auto;
}
a:link {
	color: #000;
	text-decoration: none;
}
a:visited {
	text-decoration: none;
	color: #000000;
}
a:hover {
	text-decoration: underline;
	color:#003366;
}
a:active {
	text-decoration: none;
	color:#000000;
}
img {
	border:0;
}
img.border {
	padding:2px;
	margin:2px;
	border:1px solid #ddd;
	background:#fff;
}
img.float-right {
	margin: 5px 0px 5px 15px;
	border: 1px solid #ddd;
	float:right;
}
img.float-left {
	margin: 5px 15px 5px 0px;
	border: 1px solid #ddd;
	padding:5px;
	float:left;
}
.clear {
	CLEAR: both;
}
.STYLE1 {
	color: #FFFFFF;
}
.STYLE1 a:link, .STYLE1 a:visited, .STYLE1 a:hover {
	color: #FFFFFF;
}
.STYLE2 {
	color: #0d3e6f;
	font-weight: bold;
	font-size:12px;
}
.STYLE2 a:link {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE2 a:visited {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE2 a:hover {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE2 a:active {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE3 {
	color: #0d3e6f;
	font-size:12px;
}
.STYLE3 a:link, .STYLE3 a:visited, .STYLE3 a:hover {
	color: #0d3e6f;
}
.STYLE4 {
	color: #FFFFFF;
	font-size:20px;
	line-height: 23px;
	font-family: "黑体";
}
.STYLE4 a:link, .STYLE4 a:visited, .STYLE4 a:hover {
	color: #FFFFFF;
}
.STYLE5 {
	color: #0d3e6f;
	font-size:12px;
	line-height: 16px;
}
.STYLE5 a:link, .STYLE5 a:visited, .STYLE5 a:hover {
	color: #0d3e6f;
}
.STYLE6 {
	font-size:14px;
	line-height: 16px;
}
.STYLE41 {
	font-size: 14px;
	font-weight: bold;
	line-height: 28px;
}
.STYLE42 {
	color: #287bc6
}
.STYLE42 a:link, .STYLE42 a:visited, .STYLE42 a:hover {
	color: #287bc6;
}
.STYLE43 {
	font-size: 16px;
	font-family: "黑体";
	color: #FFFFFF;
	line-height: 30px;
	padding-left: 25px;
	margin-right: 145px;
}
.STYLE44 {
	color: #0d3e6f;
	line-height: 18px;
	font-size: 16px;
	font-family: "黑体";
}
.STYLE45 {
	color: #2b89da;
	font-weight: bold;
	margin-right: 105px;
}
#footer {
	width: 967px;
	margin-right: auto;
	margin-left: auto;
	border: 1px solid #D1D1D1;
}
#footer .links {
	margin-left: 25px;
	margin-right: 25px;
	padding-top: 10px;
	padding-bottom: 10px;
}
#footer .links div {
	margin-top: 3px;
	margin-bottom: 3px;
	border-bottom-width: 1px;
	border-bottom-style: dotted;
	border-bottom-color: #CCC;
}
#footer .copyright {
	margin-right: 25px;
	margin-left: 25px;
	border-top-width: 3px;
	border-top-style: solid;
	border-top-color: #CCC;
	text-align: center;
	padding-top: 10px;
	padding-bottom: 10px;
}
.list001 {
	width:200px; margin:5px auto;
}
.list001 li {
	overflow: hidden;
	height:22px;
	line-height:22px;
}
.a2 a:link ,.a2 a:visited ,.a2 a:hover { color:#0b6488}

</style>
<script src="Scripts/AC_RunActiveContent.js" type="text/javascript"></script><input type="hidden" id="_o_dbjbempljhcmhlfpfacalomonjpalpko" data-inspect-config="3"><script type="text/javascript" src="chrome-extension://dbjbempljhcmhlfpfacalomonjpalpko/scripts/inspector.js"></script>


</head>
<body>
<style type="text/css">
* {
	padding: 0;
	margin: 0;
}
body {
	color: #000000;
	font-size:12px;
	font-family:Arial, Helvetica, sans-serif;
	background:#FFFFFF;
		width:969px;
	margin:0 auto;
}

a:link {
	color: #000;
	text-decoration: none;
}
a:visited {
	text-decoration: none;
	color: #000000;
}
a:hover {
	text-decoration: underline;
	color:#003366;
}
a:active {
	text-decoration: none;
	color:#000000;
}

.STYLE1 {
	color: #FFFFFF;
}
.STYLE1 a:link,.STYLE1 a:visited,.STYLE1 a:hover {color: #FFFFFF;}
.STYLE2 {
	color: #0d3e6f;
	font-weight: bold;
	font-size:12px;
}
.STYLE2 a:link {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE2 a:visited {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE2 a:hover {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE2 a:active {
	color: #0d3e6f;
	font-weight:bold;
}
.STYLE3 {
	color: #0d3e6f;
	font-size:12px;
}
.STYLE3 a:link,.STYLE3 a:visited,.STYLE3 a:hover {color: #0d3e6f;}

</style>
<script src="/Scripts/AC_RunActiveContent.js" type="text/javascript"></script>
<table width="969" bgcolor="#4789cd" border="0" align="center" cellpadding="0" cellspacing="1">
  <tbody><tr>
    <td height="36" background="/images/index_03.png">
   <table border="0" cellpadding="0" cellspacing="0">
        <tbody><tr>
          <td width="30">&nbsp;</td>
          <td class="STYLE1">                                   </td>
          <td width="380">&nbsp;</td>
          <td width="10">&nbsp;</td>
        </tr>
      </tbody></table></td>
  </tr>
</tbody></table>
<table width="967" border="0" align="center" cellpadding="0" cellspacing="0" style=" border-left:solid 1px #6DA6D8; border-right:solid 1px #6DA6D8">
  <tbody><tr>
    <td><img src="//palj.dbw.cn/images/palj1.jpg" width="967" height="186"></td>
  </tr>
</tbody></table>
<table width="969" bgcolor="#C0C0C0" border="0" align="center" cellpadding="0" cellspacing="1">
  <tbody><tr>
    <td background="/images/index_11.png" height="64"><table width="98%" height="48" border="0" align="center" cellpadding="0" cellspacing="0">
        <tbody><tr>
          <td align="center"><span class="STYLE2"><a href="/" target="_blank">网站首页</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fysj/fzjd/" target="_blank">平安播报</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fysj/fzsp/" target="_blank">地市动态</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fysj/jyyw/" target="_blank">见义勇为</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fysj/ffzj/" target="_blank">反腐直击</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fzlj/zhzl/" target="_blank">政法综治</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fzlj/jfcz/" target="_blank">警方传真</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fysj/jzdc/" target="_blank">平安创建</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/zfwh/" target="_blank">政法文化</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/flff/ggfb/" target="_blank">公告发布</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/flff/sszn/" target="_blank">诉讼指南</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/flff/zzfw/" target="_blank">信息公开</a></span></td>
        </tr>
        <tr>
          <td align="center"><span class="STYLE2"><a href="/fzzt/" target="_blank">精彩专题</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fzlj/jcfy/" target="_blank">检察风云</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fzlj/fytd/" target="_blank">法院天地</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fzlj/sfzc/" target="_blank">司法之窗</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fzlj/xfaq/" target="_blank">消防安全</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fzlj/jtaq/" target="_blank">交通安全</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/flff/lsjd/" target="_blank">龙江律师</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/fysj/yasf/" target="_blank">以案说法</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/flff/zcfg/" target="_blank">护航龙江</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/tpjx/" target="_blank">图片精选</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/spbb/" target="_blank">视频在线</a></span></td>
          <td align="center"><span class="STYLE2"><a href="/yc/" target="_blank">最新稿件</a></span></td>
        </tr>
      </tbody></table></td>
  </tr>
</tbody></table>
<table width="969" bgcolor="#a9ccde" border="0" align="center" cellpadding="0" cellspacing="1">
  <tbody><tr>
    <td background="/images/index_14.png" height="30"><table border="0" cellspacing="0" cellpadding="0">
      <tbody><tr>
        <td width="20">&nbsp;</td>
        <td width="610" class="STYLE3"><div id="demo3" style="overflow:hidden;height:20px;width:610px;">
            <table width="610" border="0" align="center" cellpadding="0" cellspacing="3" cellspace="0">
              <tbody><tr>
                <td nowrap="" id="demo4">
<!--enorth cms block start [ name="v5.latest" ]-->
<a href="//palj.dbw.cn/system/2023/10/17/059223987.shtml" target="_blank">冰城交警深入开展夜查整治行动 周末两天26名酒驾人员“落网”</a>
<a href="//palj.dbw.cn/system/2023/05/24/059136453.shtml" target="_blank">黑龙江省严厉打击危险废物环境违法犯罪和自动监测数据弄虚作假</a>
<a href="//palj.dbw.cn/system/2023/05/22/059134914.shtml" target="_blank">省林区公安局东京城分局：法治副校长+法治辅导员联动化解校园矛盾纠纷</a>
<a href="//palj.dbw.cn/system/2023/05/22/059134911.shtml" target="_blank">黄色“卡片”藏玄机 省林区公安局东京城分局成功侦破一起帮助网络违法犯罪“引流”案</a>
<a href="//palj.dbw.cn/system/2023/05/16/059131143.shtml" target="_blank">10起典型案例公布！</a>
<a href="//palj.dbw.cn/system/2023/04/27/059119549.shtml" target="_blank">她，荣获黑龙江省五一劳动奖章！</a>
<!--enorth cms block end [ name="v5.latest" cost="24"]--></td>
                <td nowrap="" id="demo5">
<!--enorth cms block start [ name="v5.latest" ]-->
<a href="//palj.dbw.cn/system/2023/10/17/059223987.shtml" target="_blank">冰城交警深入开展夜查整治行动 周末两天26名酒驾人员“落网”</a>
<a href="//palj.dbw.cn/system/2023/05/24/059136453.shtml" target="_blank">黑龙江省严厉打击危险废物环境违法犯罪和自动监测数据弄虚作假</a>
<a href="//palj.dbw.cn/system/2023/05/22/059134914.shtml" target="_blank">省林区公安局东京城分局：法治副校长+法治辅导员联动化解校园矛盾纠纷</a>
<a href="//palj.dbw.cn/system/2023/05/22/059134911.shtml" target="_blank">黄色“卡片”藏玄机 省林区公安局东京城分局成功侦破一起帮助网络违法犯罪“引流”案</a>
<a href="//palj.dbw.cn/system/2023/05/16/059131143.shtml" target="_blank">10起典型案例公布！</a>
<a href="//palj.dbw.cn/system/2023/04/27/059119549.shtml" target="_blank">她，荣获黑龙江省五一劳动奖章！</a>
<!--enorth cms block end [ name="v5.latest" cost="24"]--></td>
              </tr>
            </tbody></table>
        </div>
            <script>
       var speed=20
       demo5.innerHTML=demo4.innerHTML
       function Marquee()
{
              if(demo5.offsetWidth-demo3.scrollLeft<=0)
                     demo3.scrollLeft-=demo4.offsetWidth
              else
{
                     demo3.scrollLeft++
                     }
        }
              var MyMar=setInterval(Marquee,speed)
              demo3.onmouseover=function()
    {clearInterval(MyMar)}
              demo3.onmouseout=function() 
{MyMar=setInterval(Marquee,speed)}
        </script>        </td>
        <td width="55">&nbsp;</td>
        <td> <form name="form0" action="//search.dbw.cn:9001/m_fullsearch/full_search.jsp" target="_blank" method="post">
 <table border="0" cellspacing="0" cellpadding="5">
   <tbody><tr>
     <td>站内检索</td>
     <td>&nbsp;</td>
     <td><input name="keywords" type="text" value="" size="20" style=" height:20px;">
	     <input type="hidden" name="news_type_id" value="1">
            <input type="hidden" name="channel_id" value="32000000">
          <input type="hidden" name="header" value="<script src=//www.dbw.cn/js/top.js></script>">
<input type="hidden" name="footer" value="<script  src=//www.dbw.cn/js/down.js></script>"></td>
     <td>&nbsp;</td>
     <td><input name="image" type="image" value="搜索" src="/images/button_01.png" width="66" height="23" border="border"></td>
   </tr>
 </tbody></table>
 </form>

 </td>
      </tr>

    </tbody></table></td>
  </tr>
</tbody></table>

<!--enorth cms page [ enorth parse_date="2024/10/27 00:52:20.020", cost="40", server=":=$encp$=:1915cc9b91377cf467bf466f3676ea54", error_count="0"]-->








<table width="969" border="0" align="center" cellpadding="0" cellspacing="0">
  <tbody><tr>
    <td height="8" colspan="5"></td>
  </tr>
    <tr>
    <td height="8" colspan="5"></td>
  </tr>
  <tr>
	<td height="60" colspan="5">

<!--enorth cms block start [ name="ztgg1" ]-->
<a href="//palj.dbw.cn/system/2021/07/14/058679583.shtml" target="_blank">
<img src="//pic.dbw.cn/003/012/524/00301252416_fe959032.jpg" height="60" width="969" border="0">
</a>
<!--enorth cms block end [ name="ztgg1" cost="35"]-->	</td>
  </tr>
    <tr>
    <td height="8" colspan="5"></td>
  </tr>
    <tr>
    <td height="8" colspan="5"></td>
  </tr>
  <tr>
    <td width="385" rowspan="3" valign="top"><table width="385" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
        <tbody><tr>
          <td><img src="images/index_16.png" width="383" height="30"></td>
        </tr>
        <tr>
          <td bgcolor="#FFFFFF"><div style=" width:100%;FILTER: Alpha( style=1,opacity=0,finishOpacity=60,startX=0,finishX=0,startY=0,finishY=100); BACKGROUND-COLOR: #E4F0F8">
              <table width="99%" border="0" align="center" cellpadding="0" cellspacing="0" style="position:relative;">
                <tbody><tr>
                  <td height="10"></td>
                </tr>
                <tr>
                  <td height="35" align="center" bgcolor="#053973" class="STYLE4"><div style="width:383px; height:35px; line-height:35px; overflow:hidden;">
<!--enorth cms block start [ name="paljtoutiao" ]-->
<table width="100%">
<tbody><tr>
<td></td>
<td>
<a href="//palj.dbw.cn/system/2024/10/18/059376303.shtml" target="_blank">抢险排涝护民生 筑牢城市“安全堤”</a>
</td>
</tr>
</tbody></table>
<!--more-->
<!--enorth cms block end [ name="paljtoutiao" cost="48"]--></div></td>
                </tr>
                <tr>
                  <td height="10"></td>
                </tr>
                <tr>
                  <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="paljtoutiao" ]-->
<tbody><tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/zhzl/index.shtml" target="_blank">政法综治</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/02/23/059281607.shtml" target="_blank">刘惠：推进全面从严管党治警</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/fytd/index.shtml" target="_blank">法院天地</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/10/17/059375938.shtml" target="_blank">黑龙江高院召开新闻发布会通报全省法院涉农...</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/fytd/index.shtml" target="_blank">法院天地</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/10/18/059376299.shtml" target="_blank">法官手记丨多次调解破僵局 巧化“楼梯间”争议</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/zhzl/index.shtml" target="_blank">政法综治</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/10/18/059376300.shtml" target="_blank">我省召开中小学校园食品安全和膳食经费管理...</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/jfcz/index.shtml" target="_blank">警方传真</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/28/059308323.shtml" target="_blank">男子不慎遗失手包 民警快速寻回获赞</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/jtaq/index.shtml" target="_blank">交通安全</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/28/059308338.shtml" target="_blank">哈尔滨市交通局发布“五一”出行提示</a></td>
</tr>
<!--enorth cms block end [ name="paljtoutiao" cost="127"]-->                    </tbody></table></td>
                </tr>
                <tr>
                  <td height="15"></td>
                </tr>
                <tr>
                  <td height="1" bgcolor="#CCCCCC"></td>
                </tr>
                <tr>
                  <td height="15"></td>
                </tr>
                <tr>
                  <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="paljtoutiao" ]-->
<tbody><tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/fytd/index.shtml" target="_blank">法院天地</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/10/059301102.shtml" target="_blank">解决涉医矛盾纠纷“疑难杂症”！</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/jcfy/index.shtml" target="_blank">检察风云</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/10/059301094.shtml" target="_blank">伊春市嘉荫公安：清明小长假 “警”色伴你行</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/jtaq/index.shtml" target="_blank">交通安全</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/09/059300934.shtml" target="_blank">大庆交警使用无人机巡逻执法</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/fytd/index.shtml" target="_blank">法院天地</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/10/059301117.shtml" target="_blank">五常市人民法院：“快审”“速执”获点赞</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/bfjz/index.shtml" target="_blank">帮扶救助</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/09/059300920.shtml" target="_blank">民警上演“公主抱” 帮助男孩找妈妈</a></td>
</tr>
<tr>
<td width="65" height="25" class="STYLE5">[<a href="//palj.dbw.cn/fzlj/fytd/index.shtml" target="_blank">法院天地</a>]</td>
<td width="305" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/09/059300890.shtml" target="_blank">“枫桥式人民法庭”创建示范活动启动</a></td>
</tr>
<!--enorth cms block end [ name="paljtoutiao" cost="100"]-->                    </tbody></table></td>
                </tr>
                <tr>
                  <td height="10"></td>
                </tr>
              </tbody></table>
            </div></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="10"></td>
        </tr>
      </tbody></table>
      <table width="385" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
        <tbody><tr>
          <td bgcolor="#FFFFFF"><div style=" width:100%;FILTER: Alpha( style=1,opacity=60,finishOpacity=0,startX=0,finishX=0,startY=0,finishY=100); BACKGROUND-COLOR: #E4F0F8">
              <table width="100%" border="0" align="center" cellpadding="0" cellspacing="0" style="position:relative;">
                <tbody><tr>
                  <td height="32"><a href="/fysj/ffzj/" target="_blank"><img src="images/index_33.png" width="140" height="28"></a></td>
                </tr>
                <tr>
                  <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="25" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="360" class="STYLE6"><a href="//palj.dbw.cn/system/2024/10/17/059375941.shtml" target="_blank">黑龙江省佳木斯市卫生健康委员会原党组书记、主任肖明东接受纪律审查和监察调查</a></td>
</tr>
<tr>
<td width="20" height="25" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="360" class="STYLE6"><a href="//palj.dbw.cn/system/2024/06/27/059333918.shtml" target="_blank">黑龙江省伊春市水务局原党组书记、局长赵国君接受纪律审查和监察调查</a></td>
</tr>
<tr>
<td width="20" height="25" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="360" class="STYLE6"><a href="//palj.dbw.cn/system/2024/04/09/059300883.shtml" target="_blank">黑龙江省中医药科学院（省中医医院）党委书记、院长陈宏接受纪律审查和监察调查</a></td>
</tr>
<tr>
<td width="20" height="25" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="360" class="STYLE6"><a href="//palj.dbw.cn/system/2024/02/23/059281773.shtml" target="_blank">鹤岗市公安局原党委委员、副局长周大勇接受纪律审查和监察调查</a></td>
</tr>
<tr>
<td width="20" height="25" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="360" class="STYLE6"><a href="//palj.dbw.cn/system/2023/11/21/059242275.shtml" target="_blank">今年10月全省查处违反中央八项规定精神问题569起</a></td>
</tr>
<tr>
<td width="20" height="25" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="360" class="STYLE6"><a href="//palj.dbw.cn/system/2023/10/30/059230944.shtml" target="_blank">3人接受审查调查，5起典型案例被通报</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="49"]-->                    </tbody></table></td>
                </tr>
                <tr>
                  <td height="10"></td>
                </tr>
              </tbody></table>
            </div></td>
        </tr>
      </tbody></table></td>
    <td width="10" rowspan="3">&nbsp;</td>
    <td height="256" colspan="3" valign="top"><style type="text/css">
* { margin:0; padding:0; word-break:break-all; }

h1, h2, h3, h4, h5, h6 { font-size:1em; }

fieldset, img {
	border:none;
}
legend {
	display:none;
}
em, cite, th { font-style:normal; font-weight:normal; }
.mealpic01 {
	width: 210px;
	float: right;
	line-height: 22px;
	margin-bottom: 5px;
}
#ifocus {
	width:576px;
	height:256px;
	background-color: #CCCCCC;
}
#ifocus_pic {
	display:inline;
	position:relative;
	float:left;
	width:349px;
	height:256px;
	overflow:hidden;
}
#ifocus_piclist {
	position:absolute;
}
#ifocus_piclist li {
	width:349px;
	height:256px;
	overflow:hidden;
}
#ifocus_piclist img {
	width:349px;
	height:256px;
}
#ifocus_btn {
	display:inline;
	float:right;
	width:215px;
}
#ifocus_btn li {
	width:96px;
	height:74px;
	cursor:pointer;
	opacity:0.5;
	-moz-opacity:0.5;
	float: left;
	padding: 2px;
	background-color: #FFFFFF;
	margin: 3px;
	list-style-type: none;
	list-style-image: none;
}
#ifocus_btn img {
	width:86px;
	height:66px;
	border: 1px solid #CCCCCC;
}
#ifocus_btn .current {
	background-color: #0f87dd;
	height: 74px;
	width: 96px;
}
#ifocus_opdiv {
	position:absolute;
	left:0;
	bottom:0px;
	width:349px;
	height:35px;
	background:#000;
	opacity:0.5;
	-moz-opacity:0.5;
	filter:alpha(opacity=50);
}
#ifocus_tx {
	position:absolute;
	left:7px;
	bottom:4px;
	color:#FFF;
	line-height: 25px;
}
#ifocus_tx a:link {
	color:#FFF;
	font-size: 14px;
}
#ifocus_tx a:visited {
	color:#FFF;
	font-size: 14px;
}
#ifocus_tx a:hover {
	color:#FFF;
	font-size: 14px;
}
#ifocus_tx .normal {
	display:none;
}
</style>





<script type="text/javascript">
function $(id) { return document.getElementById(id); }

function addLoadEvent(func){
	var oldonload = window.onload;
	if (typeof window.onload != 'function') {
		window.onload = func;
	} else {
		window.onload = function(){
			oldonload();
			func();
		}
	}
}

function moveElement(elementID,final_x,final_y,interval) {
  if (!document.getElementById) return false;
  if (!document.getElementById(elementID)) return false;
  var elem = document.getElementById(elementID);
  if (elem.movement) {
    clearTimeout(elem.movement);
  }
  if (!elem.style.left) {
    elem.style.left = "0px";
  }
  if (!elem.style.top) {
    elem.style.top = "0px";
  }
  var xpos = parseInt(elem.style.left);
  var ypos = parseInt(elem.style.top);
  if (xpos == final_x && ypos == final_y) {
		return true;
  }
  if (xpos < final_x) {
    var dist = Math.ceil((final_x - xpos)/10);
    xpos = xpos + dist;
  }
  if (xpos > final_x) {
    var dist = Math.ceil((xpos - final_x)/10);
    xpos = xpos - dist;
  }
  if (ypos < final_y) {
    var dist = Math.ceil((final_y - ypos)/10);
    ypos = ypos + dist;
  }
  if (ypos > final_y) {
    var dist = Math.ceil((ypos - final_y)/10);
    ypos = ypos - dist;
  }
  elem.style.left = xpos + "px";
  elem.style.top = ypos + "px";
  var repeat = "moveElement('"+elementID+"',"+final_x+","+final_y+","+interval+")";
  elem.movement = setTimeout(repeat,interval);
}

function classNormal(iFocusBtnID,iFocusTxID){
	var iFocusBtns= $(iFocusBtnID).getElementsByTagName('li');
	var iFocusTxs = $(iFocusTxID).getElementsByTagName('li');
	for(var i=0; i<iFocusBtns.length; i++) {
		iFocusBtns[i].className='normal';
		iFocusTxs[i].className='normal';
	}
}

function classCurrent(iFocusBtnID,iFocusTxID,n){
	var iFocusBtns= $(iFocusBtnID).getElementsByTagName('li');
	var iFocusTxs = $(iFocusTxID).getElementsByTagName('li');
	iFocusBtns[n].className='current';
	iFocusTxs[n].className='current';
}

function iFocusChange() {
	if(!$('ifocus')) return false;
	$('ifocus').onmouseover = function(){atuokey = true};
	$('ifocus').onmouseout = function(){atuokey = false};
	var iFocusBtns = $('ifocus_btn').getElementsByTagName('li');
	var listLength = iFocusBtns.length;
	iFocusBtns[0].onmouseover = function() {
		moveElement('ifocus_piclist',0,0,5);
		classNormal('ifocus_btn','ifocus_tx');
		classCurrent('ifocus_btn','ifocus_tx',0);
	}
	if (listLength>=2) {
		iFocusBtns[1].onmouseover = function() {
			moveElement('ifocus_piclist',0,-260,5);
			classNormal('ifocus_btn','ifocus_tx');
			classCurrent('ifocus_btn','ifocus_tx',1);
		}
	}
	if (listLength>=3) {
		iFocusBtns[2].onmouseover = function() {
			moveElement('ifocus_piclist',0,-516,5);
			classNormal('ifocus_btn','ifocus_tx');
			classCurrent('ifocus_btn','ifocus_tx',2);
		}
	}
	if (listLength>=4) {
		iFocusBtns[3].onmouseover = function() {
			moveElement('ifocus_piclist',0,-776,5);
			classNormal('ifocus_btn','ifocus_tx');
			classCurrent('ifocus_btn','ifocus_tx',3);
		}
	}if (listLength>=5) {
		iFocusBtns[4].onmouseover = function() {
			moveElement('ifocus_piclist',0,-1034,5);
			classNormal('ifocus_btn','ifocus_tx');
			classCurrent('ifocus_btn','ifocus_tx',4);
		}
	}if (listLength>=6) {
		iFocusBtns[5].onmouseover = function() {
			moveElement('ifocus_piclist',0,-1292,5);
			classNormal('ifocus_btn','ifocus_tx');
			classCurrent('ifocus_btn','ifocus_tx',5);
		}
	}
}

setInterval('autoiFocus()',5000);
var atuokey = false;
function autoiFocus() {
	if(!$('ifocus')) return false;
	if(atuokey) return false;
	var focusBtnList = $('ifocus_btn').getElementsByTagName('li');
	var listLength = focusBtnList.length;
	for(var i=0; i<listLength; i++) {
		if (focusBtnList[i].className == 'current') var currentNum = i;
	}
	if (currentNum==0&&listLength!=1 ){
		moveElement('ifocus_piclist',0,-260,5);
		classNormal('ifocus_btn','ifocus_tx');
		classCurrent('ifocus_btn','ifocus_tx',1);
	}
	if (currentNum==1&&listLength!=2 ){
		moveElement('ifocus_piclist',0,-516,5);
		classNormal('ifocus_btn','ifocus_tx');
		classCurrent('ifocus_btn','ifocus_tx',2);
	}
	if (currentNum==2&&listLength!=3 ){
		moveElement('ifocus_piclist',0,-776,5);
		classNormal('ifocus_btn','ifocus_tx');
		classCurrent('ifocus_btn','ifocus_tx',3);
	}
	if (currentNum==3 && listLength!=4 ){
		moveElement('ifocus_piclist',0,-1034,5);
		classNormal('ifocus_btn','ifocus_tx');
		classCurrent('ifocus_btn','ifocus_tx',4);
	}
	
	if (currentNum==4 && listLength!=5 ){
		moveElement('ifocus_piclist',0,-1292,5);
		classNormal('ifocus_btn','ifocus_tx');
		classCurrent('ifocus_btn','ifocus_tx',5);
	}
	if (currentNum==5 && listLength!=0){
		moveElement('ifocus_piclist',0,-0,5);
		classNormal('ifocus_btn','ifocus_tx');
		classCurrent('ifocus_btn','ifocus_tx',0);
	}
	
}
addLoadEvent(iFocusChange);
</script>
<div id="ifocus">
  <div id="ifocus_pic">
	<div id="ifocus_piclist" style="left: 0px; top: -260px;">
			<ul>

<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/10/18/059376294.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/975/00301597567_83c9cc11.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
<tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/08/20/059354398.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/830/00301583033_b44f8045.jpg" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
<tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/04/08/059300356.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/539/00301553936_cd4b84a0.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
<tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/04/07/059299736.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/537/00301553731_b0622946.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
<tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/04/01/059297565.shtml" target="_blank"><img src="https://imgcdn.hljtv.com/@/catchimages/20240331/1711886971107067171.gif?imageMogr2/thumbnail/1080x%3E/strip/quality/95/ignore-error/1|imageslim" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
<tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/03/25/059294558.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/511/00301551180_615d4d8f.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="49"]-->			</ul>
	</div>
		<div id="ifocus_opdiv"></div>
		<div id="ifocus_tx">
<ul>
				<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<a href="//palj.dbw.cn/system/2024/10/18/059376294.shtml" target="_blank">金秋十月 冰城公安为秋收秋菜运输保驾护航</a>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="29"]--></li>
				<li class="current">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<a href="//palj.dbw.cn/system/2024/08/20/059354398.shtml" target="_blank">龙江公安倾警全力 筑牢夏日安全防线</a>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
				<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<a href="//palj.dbw.cn/system/2024/04/08/059300356.shtml" target="_blank">完美收官！冰城公安暖心守护未完待续……</a>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
				<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<a href="//palj.dbw.cn/system/2024/04/07/059299736.shtml" target="_blank">森林防火警钟长鸣 防灾减灾你我同行</a>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="31"]--></li>
                <li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<a href="//palj.dbw.cn/system/2024/04/01/059297565.shtml" target="_blank">安排！“尔滨”四季冰雪畅玩</a>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
				<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<a href="//palj.dbw.cn/system/2024/03/25/059294558.shtml" target="_blank">黑龙江高院召开2024年1至2月司法审判数据分析研判会商会议</a>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
	  </ul>
    </div>
  </div>
   
    <div id="ifocus_btn">
		<ul>
			<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/10/18/059376294.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/975/00301597567_83c9cc11.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
			<li class="current">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/08/20/059354398.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/830/00301583033_b44f8045.jpg" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
			<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/04/08/059300356.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/539/00301553936_cd4b84a0.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
			<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/04/07/059299736.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/537/00301553731_b0622946.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="29"]--></li>
            <li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/04/01/059297565.shtml" target="_blank"><img src="https://imgcdn.hljtv.com/@/catchimages/20240331/1711886971107067171.gif?imageMogr2/thumbnail/1080x%3E/strip/quality/95/ignore-error/1|imageslim" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="31"]--></li>
			<li class="normal">
<!--enorth cms block start [ name="pajdtp" ]-->
<table width="100%">
<tbody><tr>
<td>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><div align="center"><a href="//palj.dbw.cn/system/2024/03/25/059294558.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/511/00301551180_615d4d8f.png" border="0"></a></div></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="pajdtp" cost="30"]--></li>
		</ul>
  </div>
</div>
</td>
  </tr>
  <tr>
    <td height="10" colspan="3"></td>
  </tr>
  <tr>
    <td width="355" valign="top"><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
        <tbody><tr>
          <td bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="35"><a href="/fysj/fzjd/" target="_blank"><img src="images/index_27.png" width="140" height="28"></a></td>
              </tr>
              <tr>
                <td height="110"><table border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td width="20" height="25" align="center" bgcolor="#c6dff8"><img src="images/icon_01.png" width="3" height="3"></td>
                      <td width="320" bgcolor="#c6dff8"><span class="STYLE41">
<!--enorth cms block start [ name="v5.latest" ]-->
<a href="//palj.dbw.cn/system/2024/03/06/059286839.shtml" target="_blank">黑龙江： 春运落幕“藏蓝”身影护平安</a>
<!--enorth cms block end [ name="v5.latest" cost="24"]--></span></td>
                    </tr>

<!--enorth cms block start [ name="v5.latest" ]-->
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/01/19/059268659.shtml" target="_blank">一抹藏青蓝擦亮冬季护游“平安底色”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/01/18/059268138.shtml" target="_blank">冰城公安反诈宣传进“百年老街” 守护游客“钱袋子”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/01/09/059264546.shtml" target="_blank">中国警察节丨《平安》</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/01/02/059261603.shtml" target="_blank">元旦假期“警”相随 守护平安不“打烊”</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="56"]-->                  </tbody></table></td>
              </tr>
              <tr>
                <td height="5"></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="10"></td>
        </tr>
      </tbody></table>
      <table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
        <tbody><tr>
          <td bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="33"><a href="/fysj/fzsp/" target="_blank"><img src="images/index_36.png" width="140" height="28"></a></td>
              </tr>
              <tr>
                <td height="155"><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/23/059306317.shtml" target="_blank">优化营商环境 跑出伊春公安“加速度”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/16/059303693.shtml" target="_blank">伊春公安聚焦“三项举措”全力提升群众安全感满意度</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/10/059301211.shtml" target="_blank">伊春公安“四聚焦四到位”筑牢校园安全屏障</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/10/059301130.shtml" target="_blank">兼顾“爱”与“责任” 哈尔滨市公安局号召您做文明养犬人</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/07/059299685.shtml" target="_blank">打击整治网络谣言！通河这种宣传方式很新颖</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/01/059297589.shtml" target="_blank"> 牡铁公安多举措守护校园安全</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="46"]-->                  </tbody></table></td>
              </tr>
              <tr>
                <td height="5"></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table></td>
    <td width="10">&nbsp;</td>
    <td width="216" rowspan="3" valign="top"><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
        <tbody><tr bgcolor="#FFFFFF">
          <td><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="35" align="center"><img src="images/index_bisdh.gif" width="208" height="25"></td>
              </tr>
              <tr>
                <td>
                  <table width="100%" border="0" cellspacing="0" cellpadding="0">
      <tbody><tr>
        <td width="25">&nbsp;</td>
        <td class="a2"><a href="http:/gafw.hljga.gov.cn/" target="_blank">公安服务大厅</a></td>
        <td class="a2"><a href="//hl.122.gov.cn/" target="_blank">交通违法查询</a></td>
        <td>&nbsp;</td>
      </tr>
       <tr>
        <td height="5"></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td class="a2"><a href="//www.12309.gov.cn/nicDefault.html" target="_blank">网上举报中心</a></td>
        <td class="a2"><a href="//shixin.court.gov.cn/" target="_blank">执行信息公开</a></td>
        <td>&nbsp;</td>
      </tr>
     
    </tbody></table>
 </td>
              </tr>
              <tr>
                <td height="5"></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table><table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="6"></td>
        </tr>
      </tbody></table><table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td width="216" height="129" valign="top" background="images/index_32.png"><table width="100%" border="0" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="25">&nbsp;</td>
                <td class="STYLE2">公告板</td>
                <td width="60" height="5"><a href="/flff/ggfb/" target="_blank"><span class="STYLE42">&gt;&gt; 更多</span></a></td>
              </tr>
            </tbody></table>
            <div id="demo" style="overflow:hidden; width:216px; height:104px;">
              <div id="demo1">
               <ul class="list001">

<!--enorth cms block start [ name="v5.latest" ]-->
<li>· <a href="//palj.dbw.cn/system/2024/08/20/059354396.shtml" target="_blank">提醒！8月20日，绥化市区这些地方停电，最长停14小时</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/06/24/059332218.shtml" target="_blank">黑龙江省启动防汛四级应急响应</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/24/059318632.shtml" target="_blank">全省率先！牡丹江实现退休公积金线上办理</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/10/059313302.shtml" target="_blank">举报电话公布！黑龙江省四部门联合通告：集中整治！</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/10/059313300.shtml" target="_blank">哈尔滨市迎来降雨天气 冰城交警发布温馨提示</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/10/059313299.shtml" target="_blank">松花江进入禁渔禁捕期</a></li>
<!--enorth cms block end [ name="v5.latest" cost="52"]-->                </ul>
              </div>
              <div id="demo2">
               <ul class="list001">

<!--enorth cms block start [ name="v5.latest" ]-->
<li>· <a href="//palj.dbw.cn/system/2024/08/20/059354396.shtml" target="_blank">提醒！8月20日，绥化市区这些地方停电，最长停14小时</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/06/24/059332218.shtml" target="_blank">黑龙江省启动防汛四级应急响应</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/24/059318632.shtml" target="_blank">全省率先！牡丹江实现退休公积金线上办理</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/10/059313302.shtml" target="_blank">举报电话公布！黑龙江省四部门联合通告：集中整治！</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/10/059313300.shtml" target="_blank">哈尔滨市迎来降雨天气 冰城交警发布温馨提示</a></li>
<li>· <a href="//palj.dbw.cn/system/2024/05/10/059313299.shtml" target="_blank">松花江进入禁渔禁捕期</a></li>
<!--enorth cms block end [ name="v5.latest" cost="52"]-->                </ul>
              </div>
            </div>
            <script language="javascript"> 
var speed=80
demo2.innerHTML=demo1.innerHTML 
function Marquee(){ 
if(demo2.offsetTop-demo.scrollTop<=0) 
demo.scrollTop-=demo1.offsetHeight 
else{ 
demo.scrollTop++ 
} 
} 
var MyMar=setInterval(Marquee,speed) 
demo.onmouseover=function() {clearInterval(MyMar)} 
demo.onmouseout=function() {MyMar=setInterval(Marquee,speed)} 
</script></td>
        </tr>
      </tbody></table><table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="6"></td>
        </tr>
      </tbody></table>
      <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td align="right"><a href="mailto:pinganlongjiang@163.com" target="_blank"><img src="images/ep_wytg.gif" width="90" height="21"></a></td>
          <td width="10"></td>
          <td><a href="//palj.dbw.cn/system/2010/06/23/052581856.shtml" target="_blank"><img src="images/ep_tsxz.gif" width="90" height="21"></a></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="6"></td>
        </tr>
      </tbody></table><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
        <tbody><tr bgcolor="#FFFFFF">
          <td><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="35" align="center"><img src="images/index_bizjz.gif" width="208" height="25"></td>
              </tr>
              <tr>
                <td><table border="0" width="100%" align="center" cellpadding="0" cellspacing="0">
                <tbody><tr>
                   <td> 
<!--enorth cms block start [ name="v5.latest" ]-->
</td></tr><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2024/08/05/059349177.shtml" target="_blank">老人路边晕倒 民警及时救助</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2024/06/28/059334158.shtml" target="_blank">外省游客自驾迷路 冰城民警及时...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2024/05/27/059319802.shtml" target="_blank">“机”不可失！民警帮助学生寻...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2024/04/22/059305528.shtml" target="_blank">民警救助受伤群众 平凡“警”事...</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="33"]-->
                </tbody></table></td>
              </tr>
              <tr>
                <td height="5"></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table><table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="6"></td>
        </tr>
      </tbody></table>
      <table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
        <tbody><tr>
          <td bgcolor="#FFFFFF"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="35" align="center"><img src="images/index_41.png" width="208" height="25"></td>
              </tr>
              <tr>
                <td><table border="0" width="100%" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/10/25/059228679.shtml" target="_blank">身边的英雄 | 他，无惧火险勇救...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/05/17/059131700.shtml" target="_blank">女子半夜跳桥轻生被困江心岛 警...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/05/17/059131505.shtml" target="_blank">女游客突发疾病晕倒 冰城公安紧...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/05/06/059124512.shtml" target="_blank">八旬老人欲跳楼轻生，民警“飞...</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="51"]-->                </tbody></table></td>
              </tr>
              <tr>
                <td height="5"></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="6"></td>
        </tr>
      </tbody></table>
      
      <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td align="center">
<!--enorth cms block start [ name="ztzub" ]-->
<a href="//palj.dbw.cn/system/2019/10/16/058274836.shtml" target="_blank"><img src="//pic.dbw.cn/003/009/329/00300932927_8be74b90.jpg" width="210" height="52" border="0"></a>
<a href="//palj.dbw.cn/system/2018/04/26/057981120.shtml" target="_blank"><img src="//pic.dbw.cn/003/009/329/00300932930_2658b5e4.jpg" width="210" height="52" border="0"></a>
<!--enorth cms block end [ name="ztzub" cost="42"]--></td>
        </tr>
      </tbody></table></td>
  </tr>
  <tr>
    <td height="10" colspan="3"></td>
    <td height="10"></td>
  </tr>
  <tr>
    <td colspan="3" valign="top"><table bgcolor="#a2c0e6" width="100%" border="0" cellpadding="0" cellspacing="1">
        <tbody><tr>
          <td bgcolor="#FFFFFF"><table width="98%" border="0" align="center" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="30"><table width="100%" height="18" style="background:url(images/index_45.png) no-repeat" border="0" cellspacing="0" cellpadding="0">
                    <tbody><tr>
                      <td width="25">&nbsp;</td>
                      <td><span class="STYLE44">图片精选</span></td>
                      <td width="50" valign="bottom"><a href="/tpjx/" target="_blank"><span class="STYLE42">&gt;&gt; 更多</span></a></td>
                    </tr>
                  </tbody></table></td>
              </tr>
              <tr>
                <td height="1" background="images/index_105.png"></td>
              </tr>
              <tr>
                <td height="170">
<!--enorth cms block start [ name="v5.latest" ]-->
<table width="100%">
<tbody><tr>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2024/04/08/059300356.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/539/00301553936_cd4b84a0.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2024/04/08/059300356.shtml" target="_blank">完美收官！冰城公安暖心守护未完待续……</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2024/01/11/059265527.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/368/00301536832_6218ac3c.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2024/01/11/059265527.shtml" target="_blank">第四个“中国人民警察节” 省公安厅举行警旗升旗仪式</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2023/12/11/059251305.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/293/00301529331_34e029d4.jpg" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/12/11/059251305.shtml" target="_blank">哈尔滨市公安局道外分局聚焦“四强化”举措 全力站好平安护学岗</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2023/05/29/059140112.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/830/00301483068_b15e283c.jpg" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/05/29/059140112.shtml" target="_blank">研讨怎样讲好法院故事、如何繁荣法院文化</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2023/05/26/059138365.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/824/00301482462_9b378e16.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/05/26/059138365.shtml" target="_blank">训练场上练“精兵” 汪汪队“犬”力出击</a></span></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="v5.latest" cost="60"]--></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table></td>
    <td valign="top">&nbsp;</td>
  </tr>
</tbody></table>
<table border="0" cellspacing="0" cellpadding="0">
  <tbody><tr>
    <td height="10"></td>
  </tr>
</tbody></table>
<table width="969" border="0" align="center" cellpadding="0" cellspacing="0">
	<tbody><tr>
		<td height="60">

<!--enorth cms block start [ name="ztgg2" ]-->
<a href="//palj.dbw.cn/system/2019/05/22/058204304.shtml" target="_blank">
<img src="//pic.dbw.cn/003/010/126/00301012613_cb4ea2e7.jpg" height="60" width="969" border="0">
</a>
<!--enorth cms block end [ name="ztgg2" cost="35"]-->		</td>
	</tr>
</tbody></table>
<table width="969" style="background:url(images/index_59.png) repeat-x" border="0" align="center" cellpadding="0" cellspacing="0">
  <tbody><tr>
    <td height="5"></td>
  </tr>
  <tr>
    <td><table style="background:#E9F2F9 url(images/index_62.png) no-repeat left top" width="99%" border="0" align="center" cellpadding="0" cellspacing="0">
        <tbody><tr>
          <td height="190"><table width="100%" border="0" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td valign="top"><table width="284" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td width="284" height="30" background="images/index_67.png" bgcolor="#FFFFFF"><span class="STYLE43">平安创建</span><span class="STYLE1"><a href="/fysj/jzdc/" target="_blank">&gt;&gt;更多</a></span></td>
                    </tr>
                    <tr>
                      <td height="5"></td>
                    </tr>
                    <tr>
                      <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/09/27/059214942.shtml" target="_blank">盗窃惯犯“重操旧业” 伊春警方再次出击</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/09/27/059214940.shtml" target="_blank">大庆龙南警方及时劝阻 为群众止损2万元</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/09/27/059214936.shtml" target="_blank">富锦市公安局：多措并举夯实平安根基</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/09/27/059214931.shtml" target="_blank">同江市公安局交警大队深入开展夏季交通安全...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/09/27/059214929.shtml" target="_blank">同江市公安局多举措开展“两节”前期安全隐...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/09/25/059213706.shtml" target="_blank">大庆警方重拳出击速破四起盗窃案</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="52"]-->                        </tbody></table></td>
                    </tr>
                  </tbody></table></td>
                <td valign="top"><table width="284" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td width="284" height="30" background="images/index_67.png" bgcolor="#FFFFFF"><span class="STYLE43">以案说法</span><span class="STYLE1"><a href="/fysj/yasf/" target="_blank">&gt;&gt;更多</a></span></td>
                    </tr>
                    <tr>
                      <td height="5"></td>
                    </tr>
                    <tr>
                      <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/07/10/059166130.shtml" target="_blank">大庆市公安局连续抓获4名外省网上逃犯</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/25/059137544.shtml" target="_blank">两名司法干部将分别受审，涉嫌枉法裁判、徇...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/24/059136539.shtml" target="_blank">儿子意外离世，母亲取款时竟遭银行拒绝?</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/24/059136462.shtml" target="_blank">随意捕捞属非法 小心判刑！</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/19/059133466.shtml" target="_blank">快递丢了？有人打电话要主动赔付，小心有诈！</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/19/059133281.shtml" target="_blank">“硬核”执行 全力保障当事人胜诉权益</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="47"]-->                        </tbody></table></td>
                    </tr>
                  </tbody></table></td>
                <td><table border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td><table border="0" align="center" cellpadding="0" cellspacing="0">
                          <tbody><tr>
                            <td valign="top"><table width="284" border="0" align="center" cellpadding="0" cellspacing="0">
                                <tbody><tr>
                                  <td width="284" height="30" background="images/index_67.png" bgcolor="#FFFFFF"><span class="STYLE43">护航龙江</span><span class="STYLE1"><a href="/flff/zcfg/" target="_blank">&gt;&gt;更多</a></span></td>
                                </tr>
                                <tr>
                                  <td height="5"></td>
                                </tr>
                                <tr>
                                  <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/01/03/059262222.shtml" target="_blank">冰城公安帮助香港游客找回遗失钱包</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/12/19/059255546.shtml" target="_blank">伊春公安“三强三升”推动执法规范化建设</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/12/11/059251301.shtml" target="_blank">老人不慎摔伤 东莱民警及时出手助平安回家</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/12/11/059251300.shtml" target="_blank">电动三轮车肇事逃逸 伊春警方30小时破案</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/11/24/059244068.shtml" target="_blank">佳木斯市公安局：大雪再来袭 全警保平安</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/11/15/059239565.shtml" target="_blank">富锦公安：四项举措着力提升户政服务水平</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="45"]-->                                    </tbody></table></td>
                                </tr>
                              </tbody></table></td>
                          </tr>
                        </tbody></table></td>
                    </tr>
                  </tbody></table></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table></td>
  </tr>
</tbody></table>
<table border="0" cellspacing="0" cellpadding="0">
  <tbody><tr>
    <td height="10"></td>
  </tr>
</tbody></table>
<table width="969" border="0" align="center" cellpadding="0" cellspacing="0" style="background:url(images/gifbg002.gif) no-repeat">
  <tbody><tr>
    <td><table width="100%" height="18" border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td><span class="STYLE43">政法文化</span></td>
          <td width="70"><a href="/zfwh/" target="_blank"><span class="STYLE42">&gt;&gt; 更多</span></a></td>
        </tr>
      </tbody></table></td>
  </tr>
</tbody></table>
<table width="969" border="0" align="center" cellpadding="0" cellspacing="0" style=" border-left:solid 1px #6DA6D8; border-right:solid 1px #6DA6D8;border-bottom:solid 1px #6DA6D8">
  <tbody><tr>
    <td height="140">
<!--enorth cms block start [ name="v5.latest" ]-->
<table width="100%">
<tbody><tr>
<td width="16%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2023/04/27/059119550.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/759/00301475938_0a454184.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/04/27/059119550.shtml" target="_blank">网络微短剧《谜寻》上线播出效果良好</a></span></td>
</tr>
</tbody></table>
</td>
<td width="16%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2023/01/03/059047636.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/495/00301449571_45d3d40a.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/01/03/059047636.shtml" target="_blank">原创MV | 《信念》</a></span></td>
</tr>
</tbody></table>
</td>
<td width="16%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2022/12/30/059045268.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/489/00301448907_96b78444.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2022/12/30/059045268.shtml" target="_blank">2023雪堡开幕！牡丹江公安全力护游</a></span></td>
</tr>
</tbody></table>
</td>
<td width="16%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2022/12/21/059040317.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/474/00301447432_a410ed23.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2022/12/21/059040317.shtml" target="_blank">沁警心 润警营 冰城公安举办百场读书分享会</a></span></td>
</tr>
</tbody></table>
</td>
<td width="16%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2022/12/15/059037309.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/462/00301446260_85812038.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2022/12/15/059037309.shtml" target="_blank">佳铁公安记忆口述历史专题片《破局》</a></span></td>
</tr>
</tbody></table>
</td>
<td width="16%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td><a href="//palj.dbw.cn/system/2022/10/20/059000977.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/319/00301431925_2f27971c.png" width="122" height="86" style="padding:3px; border: solid 1px #a2c0e6 "></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td><span class="STYLE42"><a href="//palj.dbw.cn/system/2022/10/20/059000977.shtml" target="_blank">原创MV《誓言的珍贵》</a></span></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="v5.latest" cost="82"]--></td>
  </tr>
</tbody></table>
<table border="0" cellspacing="0" cellpadding="0">
  <tbody><tr>
    <td height="10"></td>
  </tr>
</tbody></table>
<table width="969" border="0" align="center" cellpadding="0" cellspacing="0">
  <tbody><tr>
    <td width="747" valign="top"><table width="100%" border="0" cellpadding="0" cellspacing="0">
        <tbody><tr>
          <td><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
              <tbody><tr>
                <td bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td height="33"><table width="100%" border="0" cellpadding="0" cellspacing="0">
                          <tbody><tr>
                            <td width="10">&nbsp;</td>
                            <td width="15"><img src="images/index_78.png" width="15" height="15"></td>
                            <td>&nbsp;</td>
                            <td class="STYLE44">政法综治</td>
                            <td width="45" class="STYLE42"><a href="/fzlj/zhzl/" target="_blank">&gt;&gt;更多</a></td>
                          </tr>
                        </tbody></table></td>
                    </tr>
                    <tr>
                      <td height="100">
<!--enorth cms block start [ name="zhzl" ]-->
<table width="340" border="0" align="center" cellpadding="0" cellspacing="0" style="margin: 5px 0;">
<tbody><tr>
<td width="90" align="center"><a href="//palj.dbw.cn/system/2024/04/10/059301102.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/541/00301554199_9a289cbc.png" width="70" height="70" style="border: solid 1px #000"></a></td>
<td width="5"></td>
<td valign="top"><span class="STYLE41"><a href="//palj.dbw.cn/system/2024/04/10/059301102.shtml" target="_blank">解决涉医矛盾纠纷“疑难杂症”！</a></span><br>
<div style="text-indent: 24px;">解决涉医矛盾纠纷“疑难杂症” 哈尔滨南岗法院成立医疗纠纷法官工作室促进医疗行业规范管理</div></td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="zhzl" cost="11"]-->
                        <table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/18/059376300.shtml" target="_blank">我省召开中小学校园食品安全和膳食经费管理突出问题专项整治工作推进会议</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/18/059376303.shtml" target="_blank">抢险排涝护民生 筑牢城市“安全堤”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/18/059376301.shtml" target="_blank">我省12个大型公共机构食堂开展“光盘行动”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/06/22/059331153.shtml" target="_blank">刘惠在省委政法委员会2024年第3次全体会议上强调 为龙江振兴提供更有力法治保障</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="39"]-->                        </tbody></table></td>
                    </tr>


                    <tr>
                      <td height="5"></td>
                    </tr>
                  </tbody></table></td>
              </tr>
            </tbody></table></td>
          <td rowspan="3" width="4"></td>
          <td><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
              <tbody><tr>
                <td bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td height="33"><table width="100%" border="0" cellpadding="0" cellspacing="0">
                          <tbody><tr>
                            <td width="10">&nbsp;</td>
                            <td width="15"><img src="images/index_78.png" width="15" height="15"></td>
                            <td>&nbsp;</td>
                            <td class="STYLE44">警方传真</td>
                            <td width="45" class="STYLE42"><a href="/fzlj/jfcz/" target="_blank">&gt;&gt;更多</a></td>
                          </tr>
                        </tbody></table></td>
                    </tr>
                    <tr>
                      <td height="100">
<!--enorth cms block start [ name="zhzl" ]-->
<table width="340" border="0" align="center" cellpadding="0" cellspacing="0" style="margin: 5px 0;">
<tbody><tr>
<td width="90" align="center"><a href="//palj.dbw.cn/system/2024/01/11/059265531.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/369/00301536977_72a1af6c.png" width="70" height="70" style="border: solid 1px #000"></a></td>
<td width="5"></td>
<td valign="top"><span class="STYLE41"><a href="//palj.dbw.cn/system/2024/01/11/059265531.shtml" target="_blank">牡丹江铁警：护游冰雪 为安全“加...</a></span><br>
<div style="text-indent: 24px;"> “已经丢失的行李找回来了，感谢咱们的好民警！”近日，黑龙江省亚布力镇，前来旅游的游客刘女士...</div></td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="zhzl" cost="16"]-->
                        <table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/18/059376296.shtml" target="_blank">户籍窗口暖人心 服务群众“零距离”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/18/059376294.shtml" target="_blank">金秋十月 冰城公安为秋收秋菜运输保驾护航</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/09/19/059366409.shtml" target="_blank">冰城民警火眼金睛识破“换装”盗窃嫌疑人</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/08/27/059357450.shtml" target="_blank">平安哈马 “警”色相随 冰城公安倾心守护平安赛道</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="36"]-->                        </tbody></table></td>
                    </tr>
                    <tr>
                      <td height="5"></td>
                    </tr>
                  </tbody></table></td>
              </tr>
            </tbody></table></td>
        </tr>
        <tr>
          <td height="4"></td>
          <td></td>
        </tr>
        <tr>
          <td><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
              <tbody><tr>
                <td bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td height="33"><table width="100%" border="0" cellpadding="0" cellspacing="0">
                          <tbody><tr>
                            <td width="10">&nbsp;</td>
                            <td width="15"><img src="images/index_78.png" width="15" height="15"></td>
                            <td>&nbsp;</td>
                            <td class="STYLE44">交通安全</td>
                            <td width="45" class="STYLE42"><a href="/fzlj/jtaq/" target="_blank">&gt;&gt;更多</a></td>
                          </tr>
                        </tbody></table></td>
                    </tr>
                    <tr>
                      <td height="100">
<!--enorth cms block start [ name="zhzl" ]-->
<table width="340" border="0" align="center" cellpadding="0" cellspacing="0" style="margin: 5px 0;">
<tbody><tr>
<td width="90" align="center"><a href="//palj.dbw.cn/system/2024/04/01/059297625.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/513/00301551301_cac0cdd0.png" width="70" height="70" style="border: solid 1px #000"></a></td>
<td width="5"></td>
<td valign="top"><span class="STYLE41"><a href="//palj.dbw.cn/system/2024/04/01/059297625.shtml" target="_blank">兰西交警开展“美丽乡村行”活动...</a></span><br>
<div style="text-indent: 24px;">为进一步深化道路交通事故预防“减量控大”工作，连日来，兰西县公安交通警察大队积极启动“春雷行...</div></td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="zhzl" cost="21"]-->
                        <table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/08/20/059354397.shtml" target="_blank">8月24日，牡丹江客运站搬迁新址！</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/08/08/059350252.shtml" target="_blank">建三江分局胜利派出所开展夏季交通安全管理工作</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/08/07/059349945.shtml" target="_blank">多部门发布气象风险预警</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/08/06/059349785.shtml" target="_blank">哈尔滨市开展公路桥梁风险隐患排查专项行动</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="38"]-->                        </tbody></table></td>
                    </tr>
                    <tr>
                      <td height="5"></td>
                    </tr>
                  </tbody></table></td>
              </tr>
            </tbody></table></td>
          <td><table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#a9ccde">
              <tbody><tr>
                <td bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td height="33"><table width="100%" border="0" cellpadding="0" cellspacing="0">
                          <tbody><tr>
                            <td width="10">&nbsp;</td>
                            <td width="15"><img src="images/index_78.png" width="15" height="15"></td>
                            <td>&nbsp;</td>
                            <td class="STYLE44">消防安全</td>
                            <td width="45" class="STYLE42"><a href="/fzlj/xfaq/" target="_blank">&gt;&gt;更多</a></td>
                          </tr>
                        </tbody></table></td>
                    </tr>
                    <tr>
                      <td height="100">
<!--enorth cms block start [ name="zhzl" ]-->
<table width="340" border="0" align="center" cellpadding="0" cellspacing="0" style="margin: 5px 0;">
<tbody><tr>
<td width="90" align="center"><a href="//palj.dbw.cn/system/2024/04/07/059299736.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/537/00301553731_b0622946.png" width="70" height="70" style="border: solid 1px #000"></a></td>
<td width="5"></td>
<td valign="top"><span class="STYLE41"><a href="//palj.dbw.cn/system/2024/04/07/059299736.shtml" target="_blank">森林防火警钟长鸣 防灾减灾你我同行</a></span><br>
<div style="text-indent: 24px;">由于森林防火的长期性和大众性，加格达奇站派出所党员民警联合森林消防支队指战员为旅客群众进行森...</div></td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="zhzl" cost="15"]-->
                        <table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/09/059300921.shtml" target="_blank">女孩崴脚被困山中 消防队员徒步救援</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/09/059300691.shtml" target="_blank">227家！齐齐哈尔：持续整治</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/07/059299742.shtml" target="_blank">黑龙江哈尔滨：消防知识进校园 安全意识“记心间”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/07/059299736.shtml" target="_blank">森林防火警钟长鸣 防灾减灾你我同行</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="33"]-->                        </tbody></table></td>
                    </tr>
                    <tr>
                      <td height="5"></td>
                    </tr>
                  </tbody></table></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="6"></td>
        </tr>
      </tbody></table>
      <table bgcolor="#a2c0e6" width="100%" border="0" cellpadding="0" cellspacing="1">
        <tbody><tr>
          <td bgcolor="#FFFFFF"><table width="98%" border="0" align="center" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td height="30"><table width="100%" height="18" style="background:url(images/index_45.png) no-repeat" border="0" cellspacing="0" cellpadding="0">
                    <tbody><tr>
                      <td width="25">&nbsp;</td>
                      <td class="STYLE44">视频在线</td>
                      <td width="50" valign="bottom"><a href="/spbb/" target="_blank"><span class="STYLE42">&gt;&gt; 更多</span></a></td>
                    </tr>
                  </tbody></table></td>
              </tr>
              <tr>
                <td height="1" background="images/index_105.png"></td>
              </tr>
              <tr>
                <td height="170">
<!--enorth cms block start [ name="v5.latest" ]-->
<table width="100%">
<tbody><tr>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td width="131" height="110" align="center" valign="top" style=" background:url(/images/index_86.png) no-repeat;"><a href="//palj.dbw.cn/system/2023/12/11/059251312.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/293/00301529334_d74ac73d.png" width="122" height="86" style="margin-top:5px"></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td style="line-height:18px;"><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/12/11/059251312.shtml" target="_blank">赤狐意外中毒 民警热心救助</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td width="131" height="110" align="center" valign="top" style=" background:url(/images/index_86.png) no-repeat;"><a href="//palj.dbw.cn/system/2023/10/27/059230032.shtml" target="_blank"><img src="//pic.dbw.cn/003/015/190/00301519022_bbe506c8.png" width="122" height="86" style="margin-top:5px"></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td style="line-height:18px;"><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/10/27/059230032.shtml" target="_blank">警方视点《秋收“警”行时》</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td width="131" height="110" align="center" valign="top" style=" background:url(/images/index_86.png) no-repeat;"><a href="//palj.dbw.cn/system/2023/06/26/059157646.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/901/00301490111_5ffbf9fd.png" width="122" height="86" style="margin-top:5px"></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td style="line-height:18px;"><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/06/26/059157646.shtml" target="_blank">少女江边轻生 民警紧急救援</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td width="131" height="110" align="center" valign="top" style=" background:url(/images/index_86.png) no-repeat;"><a href="//palj.dbw.cn/system/2023/05/11/059127738.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/786/00301478631_142493ce.png" width="122" height="86" style="margin-top:5px"></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td style="line-height:18px;"><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/05/11/059127738.shtml" target="_blank">一男子持刀伤人！当场被武警控制</a></span></td>
</tr>
</tbody></table>
</td>
<td width="20%">
<table width="135" border="0" align="center" cellpadding="0" cellspacing="0">
<tbody><tr>
<td width="131" height="110" align="center" valign="top" style=" background:url(/images/index_86.png) no-repeat;"><a href="//palj.dbw.cn/system/2023/05/04/059123057.shtml" target="_blank"><img src="//pic.dbw.cn/003/014/768/00301476876_7dcfdf26.png" width="122" height="86" style="margin-top:5px"></a></td>
</tr>
<tr>
<td height="8"></td>
</tr>
<tr>
<td style="line-height:18px;"><span class="STYLE42"><a href="//palj.dbw.cn/system/2023/05/04/059123057.shtml" target="_blank">《青春你我》：愿以青春之你我，赴万丈理想</a></span></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody></table>
<!--enorth cms block end [ name="v5.latest" cost="41"]--></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table></td>
    <td width="10"></td>
    <td valign="top"><table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td><table border="0" cellspacing="0" cellpadding="0" style="border-left:solid 1px #1e568f; border-right:solid 1px #1e568f;border-top:solid 1px #1e568f;">
              <tbody><tr>
                <td width="214" height="23" background="images/index_75.png" style="padding:8px 0 0 15px;"><span class="STYLE45">精彩专题</span></td>
              </tr>
            </tbody></table>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-left:solid 1px #a9ccde; border-right:solid 1px #a9ccde;border-bottom:solid 1px #a9ccde;">
              <tbody><tr>
                <td height="295" bgcolor="#f3fafe"><div align="center">
<!--enorth cms block start [ name="jczttp" ]-->

<!--enorth cms block end [ name="jczttp" cost="3"]--></div>
                  <table border="0" width="100%" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2022/11/07/059013439.shtml" target="_blank">【专题】学习宣传贯彻党的二十...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2022/01/11/058800560.shtml" target="_blank">【专题】致敬！新时代的龙江政...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2021/03/18/058611491.shtml" target="_blank">【专题】龙江政法队伍教育整顿...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2020/10/22/058523795.shtml" target="_blank">【专题】全省政法系统“十三五...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2020/02/06/058334405.shtml" target="_blank">【专题】坚决打赢疫情防控阻击...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2018/03/01/057938821.shtml" target="_blank">【专题】新春走基层：看龙江政...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2019/11/12/058287328.shtml" target="_blank">【专题】追记29岁因公牺牲刑警...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2018/02/22/057932632.shtml" target="_blank">【新春走基层】110指挥中心的“...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2019/10/16/058274836.shtml" target="_blank">【专题】龙江警察故事</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2019/05/22/058204304.shtml" target="_blank">【专题】黑龙江扫黑除恶在行动</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="210"]-->                  </tbody></table></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="4"></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td><table border="0" cellspacing="0" cellpadding="0" style="border-left:solid 1px #1e568f; border-right:solid 1px #1e568f;border-top:solid 1px #1e568f;">
            <tbody><tr>
              <td width="214" height="23" background="images/index_75.png" style="padding:8px 0 0 15px;"><span class="STYLE45">自助服务</span> <span class="STYLE1"><a href="/flff/zzfw/" target="_blank">更多</a></span></td>
            </tr>
          </tbody></table>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-left:solid 1px #a9ccde; border-right:solid 1px #a9ccde;border-bottom:solid 1px #a9ccde;">
              <tbody><tr>
                <td height="120" bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/09/18/059209787.shtml" target="_blank">警情通报</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/08/08/059185016.shtml" target="_blank">速览！大庆市文明行为促进条例</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/07/25/059175898.shtml" target="_blank">严阵以待！黑龙江全力备战确保...</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/06/21/059155074.shtml" target="_blank">齐齐哈尔：定了！正式公布</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/06/21/059154882.shtml" target="_blank">端午假期将至，天气提前看！</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="61"]-->                </tbody></table></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="4"></td>
        </tr>
      </tbody></table>
      
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>
          <td height="6"></td>
        </tr>
      </tbody></table>
      <table border="0" cellspacing="0" cellpadding="0">
        <tbody><tr>


          <td><table border="0" cellspacing="0" cellpadding="0" style="border-left:solid 1px #1e568f; border-right:solid 1px #1e568f;border-top:solid 1px #1e568f;">
              <tbody><tr>
                <td width="214" height="23" background="images/index_75.png" style="padding:8px 0 0 15px;"><span class="STYLE45">龙江律师</span> <span class="STYLE1"><a href="/flff/lsjd/" target="_blank">更多</a></span></td>
              </tr>
            </tbody></table>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-left:solid 1px #a9ccde; border-right:solid 1px #a9ccde;border-bottom:solid 1px #a9ccde;">
              <tbody><tr>
                <td height="120" bgcolor="#f3fafe"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/05/30/059140411.shtml" target="_blank">大庆市女大学生被AI换脸恶搞 这...</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/05/25/059137784.shtml" target="_blank">普法民法典：夫妻一方借别人的...</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/05/15/059130153.shtml" target="_blank">野生鱼仅4斤左右，为何能构成犯...</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2023/04/30/059121429.shtml" target="_blank">252名“新劳动者”享受“法援”</a></td>
</tr>
<tr>
<td width="20" height="20" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="190"><a href="//palj.dbw.cn/system/2022/09/21/058979763.shtml" target="_blank">婚礼录像被婚庆公司弄丢，有权...</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="42"]-->                  </tbody></table></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table></td>
  </tr>
</tbody></table>
<table border="0" cellspacing="0" cellpadding="0">
  <tbody><tr>
    <td height="10"></td>
  </tr>
</tbody></table>
<table width="969" style="background:url(images/index_59.png) repeat-x" border="0" align="center" cellpadding="0" cellspacing="0">
  <tbody><tr>
    <td height="5"></td>
  </tr>
  <tr>
    <td><table style="background:#ffffff url(images/index_94.png) no-repeat left top" width="99%" border="0" align="center" cellpadding="0" cellspacing="0">
        <tbody><tr>
          <td height="190"><table width="100%" border="0" cellpadding="0" cellspacing="0">
              <tbody><tr>
                <td><table width="284" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td width="284" height="30" bgcolor="#FFFFFF" style="background:url(images/index_96.png) no-repeat;"><span class="STYLE43">法院天地</span><span><a href="/fzlj/fytd/" target="_blank">&gt;&gt;更多</a></span></td>
                    </tr>
                    <tr>
                      <td height="5"></td>
                    </tr>
                    <tr>
                      <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/21/059377287.shtml" target="_blank">《人民法院报》头版丨吉黑两地联合发布东北...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/21/059377286.shtml" target="_blank">第十三期丨学习贯彻党的二十届三中全会精神...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/18/059376299.shtml" target="_blank">法官手记丨多次调解破僵局 巧化“楼梯间”争议</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/10/17/059375938.shtml" target="_blank">黑龙江高院召开新闻发布会通报全省法院涉农...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/09/30/059370716.shtml" target="_blank">《人民法院报》 | 加强生态保护 守护绿水青山</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/09/30/059370715.shtml" target="_blank">我爱你中国丨寻访红色记忆 描绘锦绣山河</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="58"]-->                        </tbody></table></td>
                    </tr>
                  </tbody></table></td>
                <td><table width="284" border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td width="284" height="30" bgcolor="#FFFFFF" style="background:url(images/index_96.png) no-repeat;"><span class="STYLE43">检察风云</span><span><a href="/fzlj/jcfy/" target="_blank">&gt;&gt;更多</a></span></td>
                    </tr>
                    <tr>
                      <td height="5"></td>
                    </tr>
                    <tr>
                      <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/10/059301094.shtml" target="_blank">伊春市嘉荫公安：清明小长假 “警”色伴你行</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/11/28/059245610.shtml" target="_blank">庆安县检察院创新探索工作机制 以法治之力守...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/10/27/059230042.shtml" target="_blank">齐齐哈尔：讷河市检察院筑牢未成年人保护网</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/26/059138310.shtml" target="_blank">首批“小客人”感受“法”的力量</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/25/059137442.shtml" target="_blank">全国人大代表刘蕾：持续关注公益诉讼检察工作</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/05/23/059135851.shtml" target="_blank">五方合力促调解 释法明理化纠纷</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="62"]-->                        </tbody></table></td>
                    </tr>
                  </tbody></table></td>
                <td><table border="0" align="center" cellpadding="0" cellspacing="0">
                    <tbody><tr>
                      <td><table border="0" align="center" cellpadding="0" cellspacing="0">
                          <tbody><tr>
                            <td><table width="284" border="0" align="center" cellpadding="0" cellspacing="0">
                                <tbody><tr>
                                  <td width="284" height="30" bgcolor="#FFFFFF" style="background:url(images/index_96.png) no-repeat;"><span class="STYLE43">司法之窗</span><span><a href="/fzlj/sfzc/" target="_blank">&gt;&gt;更多</a></span></td>
                                </tr>
                                <tr>
                                  <td height="5"></td>
                                </tr>
                                <tr>
                                  <td><table border="0" align="center" cellpadding="0" cellspacing="0">

<!--enorth cms block start [ name="v5.latest" ]-->
<tbody><tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/04/08/059300267.shtml" target="_blank">发挥“桥头堡”作用，打造百姓家门口的“司...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/03/13/059289945.shtml" target="_blank">“厚植法治土壤 优化法律服务” 黑龙江省司...</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/03/11/059288856.shtml" target="_blank">黑龙江法院让司法之光温暖每一位劳动者</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2024/02/21/059280790.shtml" target="_blank">浪漫“尔滨”背后的司法“锦囊”</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/11/13/059238721.shtml" target="_blank">雪天执行“不打烊”， 司法为民暖人心</a></td>
</tr>
<tr>
<td width="20" height="23" align="center"><img src="images/icon_01.png" width="3" height="3"></td>
<td width="320"><a href="//palj.dbw.cn/system/2023/11/13/059238486.shtml" target="_blank">黑龙江省监狱管理局召开省属监狱系统党建暨...</a></td>
</tr>
<!--enorth cms block end [ name="v5.latest" cost="73"]-->                                    </tbody></table></td>
                                </tr>
                              </tbody></table></td>
                          </tr>
                        </tbody></table></td>
                    </tr>
                  </tbody></table></td>
              </tr>
            </tbody></table></td>
        </tr>
      </tbody></table></td>
  </tr>
</tbody></table>
<table border="0" cellspacing="0" cellpadding="0">
  <tbody><tr>
    <td height="10"></td>
  </tr>
</tbody></table>
<div id="footer">
  <div class="links">


</div>
<strong>友情链接</strong> <a href="//www.hljcourt.gov.cn/" target="_blank">黑龙江省法院</a>

  </div>
<table height="100">
<tbody><tr>
	<td height="100">
<p>  </p>	
	</td>
</tr>
</tbody></table>
<p>    </p>	
<!--enorth cms page [ enorth parse_date="2023/06/05 10:30:42.042", cost="0", server=":=$encp$=:9a95fdc7e5bcea637d4eb8f4324c77ab", error_count="0"]-->
<script type="text/javascript">
var _bdhmProtocol = (("https:" == document.location.protocol) ? " https://" : " //");
document.write(unescape("%3Cscript src='" + _bdhmProtocol + "hm.baidu.com/h.js%3F51e9cf5878d79a0837d9d0185025ad99' type='text/javascript'%3E%3C/script%3E"));
</script><script src=" https://hm.baidu.com/h.js?51e9cf5878d79a0837d9d0185025ad99" type="text/javascript"></script>
<div style="display:none">
<script type="text/javascript">document.write(unescape("%3Cscript src='//tongji.dbw.cn/webdig.js?z=1' type='text/javascript'%3E%3C/script%3E"));</script><script src="//tongji.dbw.cn/webdig.js?z=1" type="text/javascript"></script>
<script type="text/javascript">wd_paramtracker("_wdxid=000000000000000000000000000000000000000000")</script>
</div>



</body></html>
"""

# 使用BeautifulSoup解析HTML
# soup = BeautifulSoup(html_content, 'html.parser')
 
# 提取网页中的文本内容
# 这里使用strip=True来去除每行末尾的空白字符，包括换行符
# 使用joinlines=True来将所有文本合并为一个长字符串，去除中间的空白行
# text = '\n'.join(soup.stripped_strings)
# text = """
# 身在最北方 心向党中央丨吕金刚：让装备制造业“皇冠上的明珠”更闪亮-龙江看天下-东北网
# ===============        

# [![Image 1](https://www.dbw.cn/images/2018/logo-new.gif)](https://www.dbw.cn/)

# [![Image 2](https://ljktx.dbw.cn/images/ljktx-logo.jpg)](https://ljktx.dbw.cn/index.shtml)

# *   [时政要闻](https://ljktx.dbw.cn/szyw/)
# *   [政务•政策](https://ljktx.dbw.cn/ljtime/zwuzce/)
# *   [问政•亮剑](https://ljktx.dbw.cn/ljtime/wzhenglj/)
# *   [本网原创](https://ljktx.dbw.cn/ljtime/benwyc/)
# *   [本网动态](https://ljktx.dbw.cn/ljtime/benwdt/)
# *   [龙江地市](https://ljktx.dbw.cn/ljtime/ljdis/)
# *   [龙广电融媒矩阵](https://ljktx.dbw.cn/lgdrmjz/)

# 您当前的位置 ： [东北网](https://www.dbw.cn/index.shtml)  >  [龙江看天下](https://ljktx.dbw.cn/index.shtml)  >  [龙江时间](https://ljktx.dbw.cn/ljtime/index.shtml)  >  [看龙江](https://ljktx.dbw.cn/ljtime/kanlj/index.shtml)

# 身在最北方 心向党中央丨吕金刚：让装备制造业“皇冠上的明珠”更闪亮
# =================================

# 时间：2024-10-25 08:03:30　 来源：黑龙江日报　 作者：

# **黑龙江日报10月25日讯** 高温、高压、高转速下可靠、持久的运转，造就了航空发动机和燃气轮机极高的技术壁垒，被誉为装备制造业“皇冠上的明珠”。

# 当今世界，仅有包括中国在内的少数几个国家具备独立自主研制“两机”的能力，这代表着一国装备制造业的最高技术水平。

# 18年前，吕金刚入职哈尔滨城林科技股份有限公司，那时我国的“两机”研制正处于起步阶段。他由此一头扎进“两机”配套设备的设计、研制工作中，怀揣着激情、热爱和浓浓的科技报国情，以精细严谨、勇攀高峰的创新精神，逐渐成长为正高级工程师、行业专家、公司总经理，并带领企业成为我国中小型燃气轮机配套设备和航空发动机试车台空气动力系统配套设备技术实力最强的企业，成为我国“两机”发展中的重要一环。

# **因热爱而钻研 因钻研而成长**

# 1982年出生的吕金刚是山东省威海市人，2002年考入黑龙江八一农垦大学工程学院农业机械化及其自动化专业，由此开启了他扎根最北方的人生旅程。

# 2006年7月，吕金刚入职城林科技做设计工程师。喜欢设计、喜欢钻研的吕金刚说，他很幸运从事了自己喜欢的职业，更幸运的是他赶上了我国推进“两机”发展的时代。

# 在这样的时代背景下，入职不久后，吕金刚参与了国家863计划重型燃气轮机发电机组配套辅机系统的研制。这是我国首台重型燃气轮机发电机组，一切从零开始，而且对配套辅机系统的要求是不但要满足气动、噪声和燃机运行的所有需求，还要求可拆卸、反复组装。

# “这个要求是非常高的，当时大部分机组都是一次成型，后续搬迁时辅助机系统就不能用了，特别是高温高压的部件，涉及到耐温、膨胀、风载相结合等复杂要求。”吕金刚回忆说，那时印象最深刻的就是加班加点、反复试验，令他最兴奋的事情就是参加评审会。

# 在吕金刚看来，参加评审会是提高技术水平的最好机会。有公司的前辈、有行业专家，尤其是作为国家863项目，参加评审会的还会有我国“两机”顶级专家。在评审会中，他如饥似渴地吮吸着知识的甘霖，快速成长为行业精英。

# 从参与863计划项目起，吕金刚就像上了弦的发条，在“两机”世界里探索、攻坚，取得一个个零的突破，解决掉一个个“卡脖子”问题，为我国的“两机”发展贡献青春和智慧。

# **始终参与技术工作 逐浪行业最前沿**

# 参与国内第一套应用在海上平台自主燃气轮机发电机组的辅机系统、国内第一套应用在西气东输的自主燃气轮机驱动压缩机辅机系统、国内第一套应用在自主燃气轮机出口项目的辅机系统、国产第一台25MW级移动电源车、国产第一台燃气轮机压裂车、国产第一台110MW级重型燃气轮机发电机组辅机系统的研制，以及近20年内大部分国家航空发动机重点型号研制的条件建设……说起自己的工作成就，吕金刚最骄傲的是参与“两机”各重点型号的研制，创造了很多的“第一”，在这些“大国重器”的诞生中洒下自己的心血和汗水。

# 2007年末，入职不到两年的吕金刚作为主设计师带着入职刚一年的同事，承担起了燃气轮机自洁式空气过滤系统的自主设计工作。

# 当时国内使用的这一产品主要是国外品牌，自主设计上没有成型的经验可借鉴。于是大量的查资料、计算，反复试验，到国外产品现场进行实地测量和性能分析，搜集用户设计意见，多次开评审会不断修正。

# 经过一年多的艰辛攻坚，吕金刚带领同事终于完成了我国首台燃机用卧式自清洁过滤系统，取得自主知识产权，并成功应用在中海油东方石油平台上。

# “如果说发动机是一套燃气轮机机组‘五脏六腑’中的‘心脏’，那么箱体、过滤系统、通风系统、进气系统、排气系统、消音系统等则是机组的其它脏器，而这些均是由城林科技研制。”吕金刚对此深感自豪。

# 先后担任设计员、项目经理、项目部长、市场开发部经理、营销总监、东北大区经理、大客户事业部总经理、哈尔滨公司总经理等职，但无论在哪一个岗位上，吕金刚始终参与技术工作，目前还是公司的总设计师。他还参加了国家及行业标准的制定，是国家标准GB50454-2020《航空发动机试车台设计标准》的主要起草人员之一，国家电力行业标准DLT 5829-2021《户内配电变压器振动与噪声控制工程技术规范》的主要起草人员之一。

# **懂技术 善经营 会管理**

# “以市场为导向，以客户为中心”“敢于创新，挑战不可能和旧习惯”……这些标注在城林科技企业文化墙上的文字，凝结着吕金刚多年的技术钻研积累、市场打拼经验和管理岗位砺炼。

# “2020年哈尔滨公司的产值是八九千万元，今年预计将突破5亿元，可以说吕总带领公司实现了跨越式增长。”城林科技营销总监孔繁宇告诉记者，2020年吕金刚接任总经理时提出的发展目标，到目前都一一实现，当时大家都认为他的想法太超前、不现实。

# 担任总经理后，吕金刚开始了大刀阔斧的改革。调整管理层人员、增加就业岗位、改变薪酬制度，2022年，他力主投资5000万元建设了三期厂房，使企业产能大幅提升，为公司后续发展争先机、拓空间、蓄能量。

# “这几年公司引进了很多研发人才，补充了电气、液压等专业性人才，为公司的持续创新提供智力支撑。”城林科技副总经理牛东风介绍，吕金刚主张从企业产品行业特色经营理念入手，扎根钻研企业的专长建设，带领企业打造成为国家级专精特新重点“小巨人”,并加强了绿色化数字化车间建设，获评国家级绿色工厂企业；同时严抓企业产品质量，带领企业先后获得黑龙江省制造业单项冠军、技术创新示范企业、企业技术中心、质量标杆、数字化示范标杆等称号，完成了6个黑龙江省认定的首台套产品。

# 目前，城林科技中小型燃气轮机辅机系统和航空发动机试车台空气动力系统的全国市场占有率都达60%以上，在行业内是名副其实的NO.1。

# **记者手记**

# 从一名普通的设计工程师到正高级工程师，吕金刚用了18年。

# 采访中，记者深刻地感受到，一系列成绩的背后，是吕金刚那专注、严谨的科学精神。

# 80后的吕金刚，对钻研技术的热爱已经刻在了骨子里。大学刚毕业时，回到宿舍就是打游戏，他感到很空虚，于是下班后他不再先回宿舍，而是留在单位学习、查资料、研究项目案例；担任总经理后，他白天开会、研讨、安排各种事务、与客户沟通，晚上则静下来思考、看材料、研究项目遇到的难题，公司的重大项目他都是参与者，他也是公司掌握核心技术最多的人。

# 城林科技研发负责人邵春望告诉记者，在竞标航空发动机试车台的方案介绍环节，吕金刚会根据不同型号发动机的特性，提出产品的技术参数和性能指标，当客户提出质疑时，吕金刚则会拿出大量的数据和理论支撑，一步一步说服客户，而这些客户都是行业内的专家。吕金刚的自信来源于多年积累的丰富经验，也来源于他持续不断的学习和对每一个参与项目的数据实测和钻研。

# 专注，是一种追求上进的态度，是一份精益专业的执着，是一个不负职守的信念。唯其专注、始得玉成，正是秉持这份专注，吕金刚深度沉浸、快速成长。

# 责任编辑：王聪

# ![Image 3](https://www.dbw.cn/images/2018/logo-di.gif)  
# [联系我们](https://ljktx.dbw.cn/lxwm/index.shtml) 严格遵守保密法律法规，严禁在互联网发布涉密信息。  
# 黑龙江东北网络台版权所有 Copyright◎2001-2017 WWW.DBW.CN　All Rights Reserved.  
# 增值电信业务经营者证件号：黑B2-20080973-1 国新网许可证编号：2312006001　 哈公网监备23010002003717号  
# 广告经营许可证号：2301000000007 广播电视节目制作经营许可证：黑字第083号　 黑龙江仁大律师事务所　孙维涛律师  
  
# ![Image 4](https://www.dbw.cn/images/2018/di-logo01.jpg)　![Image 5](https://www.dbw.cn/images/2018/di-logo02.jpg)　![Image 6](https://www.dbw.cn/images/2018/di-logo03.jpg)  
  
# ![Image 7](https://www.dbw.cn/images/2018/di-logo04.jpg)

# """


# (REMOVE <SCRIPT> to </script> and variations)
SCRIPT_PATTERN = r'<[ ]*script.*?\/[ ]*script[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML <STYLE> to </style> and variations)
STYLE_PATTERN = r'<[ ]*style.*?\/[ ]*style[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML <META> to </meta> and variations)
META_PATTERN = r'<[ ]*meta.*?>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML COMMENTS <!-- to --> and variations)
COMMENT_PATTERN = r'<[ ]*!--.*?--[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML LINK <LINK> to </link> and variations)
LINK_PATTERN = r'<[ ]*link.*?>'  # mach any char zero or more times

# (REPLACE base64 images)
BASE64_IMG_PATTERN = r'<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>'

# (REPLACE <svg> to </svg> and variations)
SVG_PATTERN = r'(<svg[^>]*>)(.*?)(<\/svg>)'


def replace_svg(html: str, new_content: str = "this is a placeholder") -> str:
    return re.sub(
        SVG_PATTERN,
        lambda match: f"{match.group(1)}{new_content}{match.group(3)}",
        html,
        flags=re.DOTALL,
    )


def replace_base64_images(html: str, new_image_src: str = "#") -> str:
    return re.sub(BASE64_IMG_PATTERN, f'<img src="{new_image_src}"/>', html)


def has_base64_images(text: str) -> bool:
    base64_content_pattern = r'data:image/[^;]+;base64,[^"]+'
    return bool(re.search(base64_content_pattern, text, flags=re.DOTALL))


def has_svg_components(text: str) -> bool:
    return bool(re.search(SVG_PATTERN, text, flags=re.DOTALL))


def clean_html(html: str, clean_svg: bool = False, clean_base64: bool = False):
    html = re.sub(SCRIPT_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(STYLE_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(META_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(COMMENT_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(LINK_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

    if clean_svg:
        html = replace_svg(html)

    if clean_base64:
        html = replace_base64_images(html)

    return html


system_prompt = """
your task is extract title.
"""


response = client.chat.completions.create(
    model="reader-lm-1.5q",
    messages=[
        {
            "role": "system", 
            "content": system_prompt
        },
        {
            "role": "user", 
            "content": clean_html(html_content)
        }
    ],
    temperature=0,
    top_p=0.5,
    extra_body={
        "repetition_penalty": 1.08,
        "presence_penalty": 0.25,
        "top_k":-1,
        # "guided_json": guided_json_format
    },
    # max_length=4096,
)
import json
# rs = json.loads(response.choices[0].message.content)
print(response.choices[0].message.content)
tag = response.choices[0].message.content
# import bs4
# # 创建 BS4 对象
# soup = bs4.BeautifulSoup(html_content,  'html.parser')
# from lxml import etree 

# def get_before_second_slash(s):
#     parts = s.split('/')
#     return '/' + parts[1] + '/' + parts[2]

# rtag = get_before_second_slash(tag)
# print(rtag)
# dom = etree.HTML(str(soup))    

# print(dom.xpath(rtag)[0].innerText)

# # # 使用 XPath 表达式提取数据
# # results = soup.XPath(tag)

# # # 遍历结果
# # for result in results:
# #     print(result.text)

# # print(text[rs['start']: rs['end']])
# # print(rs)
