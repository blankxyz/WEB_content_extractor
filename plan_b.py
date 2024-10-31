from htmldate import find_date
from trafilatura.settings import Extractor
import mysql.connector
from bs4 import BeautifulSoup, Comment
html_content = """
<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <meta http-equiv="pragma" content="no-cache">
                <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
                <meta http-equiv="expires" content="0">
		<meta name="viewport" content="width=1200">
                <meta name="viewport" content="width=device-width,height=device-height, user-scalable=no,initial-scale=1, minimum-scale=1, maximum-scale=1,target-densitydpi=device-dpi">
		<meta name="apple-mobile-web-app-capable" content="yes">
		<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
                <meta name="keywords" content="">
		<title>聚力攻坚 | 全省固定资产投资 实现量的合理增长和质的有效提升-东北新闻网</title>
		<meta name="keywords" content="辽宁东北新闻门户">
		<meta itemprop="name" content="辽宁东北新闻门户">
		<link href="/channel-home/nen/css/index.css" rel="stylesheet" type="text/css">
		<link href="/channel-home/nen/css/content_bd_sz.css?v=1.0.2" rel="stylesheet" type="text/css">
    <link rel="icon" type="image/png" sizes="16x16" href="/channel-home/nen/images/logoico.png"/>
    <link rel="icon" type="image/png" sizes="32x32" href="/channel-home/nen/images/logoico32.png">
    <link rel="icon" type="image/png" sizes="48x48" href="/channel-home/nen/images/logoico48.png">
    <link rel="icon" type="image/png" sizes="96x96" href="/channel-home/nen/images/logoico96.png">
    <link rel="apple-touch-icon-precomposed" sizes="180x180" href="/channel-home/nen/images/logoico180cir.png">
                <script type="text/javascript" src="/channel-home/nen/js/index20210608.js"></script>
<script src="/channel-home/nen/js/jquery.min.js"></script>
                <script src="https://res.wx.qq.com/open/js/jweixin-1.0.0.js"></script>
                <script src="/console/js/share.js"></script>
		<style type="text/css">
                        .list_sz body {overflow:hidden;}
                        .prism-big-play-btn {margin-left:calc(50% - 54px) !important;}
			* {
		box-sizing:border-box;
	}
	html {
	    font-size: calc(100vw / 18.75);
	}
	body {
	  -webkit-text-size-adjust: none;
	  color: #000;
	  font: 0.14rem/1.8 "Microsoft Yahei", -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", STHeiti, "Microsoft Yahei", Tahoma, Simsun, sans-serif;
	}
html {background:none;}
   video { width:700px;}
.list {
                        width: 100%;
                        float: left;
                        padding-left: 0;
                        padding-bottom: 20px;
                    }
                .list p {
                        margin: 8px 0;
                        width: 100%;
                        text-align: justify;
                    }
.list_h_wx {
			position: relative;
			width: 100px;
			line-height: 40px;
			height: 40px;
			top: -50px;
			left: 1100px;
			z-index: 9;
			display: flex;
		}

		.list_h_wx p {
			line-height: 30px;
			float: left;
		}

		.list_h_wx img {
			height: 35px;
			float: left;
			margin-top: 5px;
		}
		
		.ct {
                        width:100%;
			position: relative;
                        background:#ffffff;
		}
		
#qrcode {
             width: 120px;
    height: 120px;
    position: absolute;
    right: -132px;
    top: -70px;
}
.list_h h4 {
    width: 100%;
    line-height: 36px;
    float: left;
    text-align: center;
    margin: 0px !important;
    border-bottom: 1px solid #0052B2;
    padding-bottom:5px;}

.list_h {
    width: 100%;
    height: auto;
        border-bottom: 0px solid #0052B2;
}	



.bg_topbg {
    width: 100%;
    height: 65px;
    background: url(http://ln.nen.com.cn/channel-home/nen/images/bg_bg.jpg) left top repeat-x;
    overflow: hidden;
}
 .redbg {
   
  margin:0px auto !important;
    font-size:0px;
   
}  
.list {
    width: 100%;
    padding-top: 80px;
    padding-bottom: 20px;
}
.list ul li {
    width: 100%;
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
    padding-bottom: 10px;
    padding-left:20px;
    border-bottom: 1px solid #eeeeee;
}
.list ul li::before {
    content: "";
    width: 5px;
    height: 5px;
    background: #050505;
    border-radius: 50%;
    position: absolute;
    left: 0;
    top: 14px;
    -webkit-transform: translateY(-50%);
    -moz-transform: translateY(-50%);
    -ms-transform: translateY(-50%);
    -o-transform: translateY(-50%);
    transform: translateY(-50%);
}
.list ul li a {
    max-width: 680px;
    letter-spacing: 2px;
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 0;
    color:#050505;
    display: block;
    float: left;
}
.list ul li span {
    font-size: 16px;
    color: #888;
    line-height: 36px;
    display: block;
    float: right;
    width:200px;
}
.list h4 {
    color: #0052b2;
    font-size: 24px;
    border-bottom: 4px solid #d5d5d5;
    padding-left: 5px;
    padding-bottom: 10px;
}
.list h4 span {
    border-left: solid 2px #5252b2;
    padding-left: 15px;
}
 @media (min-device-width:320px) and (max-width:689px), (max-device-width:480px)
 {

  .redbg {
    text-align: left;
    color: rgb(255, 255, 255);
    width:1000px;
    height: 2.3em;
    font: 2.3em/230% 微软雅黑;
    background: #cc0000;
    margin: 0px auto !important;
}  
body {
	background:none;
	margin:0 auto;
	color:#000;
}
.w1280 {
    width: 100vw;
}
.t_fbh_snr {
		    margin: 1px auto 0px;
			padding:1rem;
		}
		.xwzw_t3 {
		    padding: 30px 0 40px 0;
		    margin: 70px 0 0 0;
		}
		.xwzw_title {
		    font-size: 1.2rem;
		    padding: 0;
		}
.ph-body .main, .ct {
    width: 100%;
    margin: 0 auto;
    clear: both;
}

.list_sz {
    width: 98%;padding-left: 20px;
  
 
}
.list_sz p {
   font: normal 2.2em/200% 微软雅黑;
    margin: 8px 0;width: 900px;padding-left: 25px;text-align: justify;
}

.footer {
    width: 1000px;
    margin: 0 auto;
    border-top: none;
    clear: both;
    overflow: hidden;
}



.biaoz2 {
    width: 1000px;
    float: left;
    color: red;
    text-align: center;
    padding-bottom: 10px;
    border-bottom: 1px solid #0052B2;
}

.list_sz span {
     text-align: right;
    padding-right:50px;  font: bold 2em/150% 微软雅黑;
 width: 1000px;
}


.bd h2 {
     font: bold 1.3em/150% 微软雅黑;
    font-weight: bold;
    color: #7d7d7d;
    padding-bottom: 25px;
    border-bottom: 1px solid #0052B2;
 padding-left: 35px

}



.bd {
    width: 1000px;
    float: left;
    padding: 0 !important;
}

.list_h 

{
    width: 100%;
    height: auto;
    border-bottom:0px solid #0052B2;
}

.list_h h2 {
   
     text-align: left;
   font: bold 1.8em/150% 微软雅黑;
    color: #18559f;
    width:100%;
border-bottom:0px solid #0052B2;

padding-bottom:20px;
}



    
 .logoh{ display:none;}
.head{ display:none;}   
  .bg_topbg { display:none;} 
 .ph-bd { display:none;}  
   .c { width:1000px; } 
.info  { display:none;}
.w1200 { display:none;}
.list_h h4{ line-height: 36px;
    float: left; font: 1em/150% 微软雅黑;letter-spacing:1px;
    text-align: center;
    margin: 0px !important;
    border-bottom: 1px solid #0052B2;
    padding-bottom: 20px;}

 .list_h h3{  
        font: 0.9em/150% 微软雅黑;
    float: left;
    width: 100%;
    line-height: 55px;
    text-align:justify;
    text-indent: 2em;
    color: #504b4b;
    padding-bottom: 20px;
}
.list_h_wx,.sharewx { display:none;}
.list p {
                        margin: 8px 0;
                        width: 100%;
                        text-align: justify;
                    }
}
@media screen and (min-width:0px) and (max-width: 915px) {
.list ul li a {
    display: block;
    float: none;
}
.list ul li span {
    display: block;
    float: none;
}
iframe {width:100%;max-height:220px;margin:0 auto;}
}
		</style>
	</head>
	<body style="background:#f4f4f4;">
		
	<!DOCTYPE html>
<html>
	<head>
                <meta http-equiv="pragma" content="no-cache">
                <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
                <meta http-equiv="expires" content="0">
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<meta name="apple-mobile-web-app-capable" content="yes">
		<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
                
		<title>${channel_name!""}</title>
		<meta name="keywords" content="东北新闻网">
		<meta itemprop="name" content="东北新闻网">
		<style type="text/css">
.ph-bd {
    background: #f4f4f4;
    padding: 15px 0;    
}
.ph-bd-top {
    background: #fcfcfc;
    padding: 15px 0;
}
.logoh {
    width: 1280px;
    height: auto;
    clear: both;
    overflow: hidden;
    margin: 0 auto 0;
    position: relative;
    background:none;
    
}
.logow{width:310px;float:left;}
.logow img{width:310px;height:74px;}
.logo {
    width: 315px;
    height: 85px;
    background: url(/channel-home/nen/images/logo.png) left 3px no-repeat;
    float: left;
}
.nav {
    width: 1200px;
    height: 113px;
    clear: both;
    margin: 0 auto 10px;
    position: relative; 
}

.navBox {
    width:800px;
    height:auto;
    line-height:25px;
    float:left;
    font-size:18px;
    margin-top: 10px;
    display:flex;
    flex-wrap:wrap;
    margin-left: 10px;
}
.navBox a {
    flex-grow:0;
    flex-shrink:0;
    flex-basis:auto;
    font-size: 18px;
    text-align:left;
}
.navBox a:nth-of-type(1),.navBox a:nth-of-type(4),.navBox a:nth-of-type(5),.navBox a:nth-of-type(6),.navBox a:nth-of-type(7),.navBox a:nth-of-type(8) {
    flex-basis:66px;
}
.navBox a:nth-of-type(2) {
    flex-basis:107px;
}
.navBox a:nth-of-type(3) {
    flex-basis:105px;
}
.navBox a:nth-of-type(9) {
    flex-basis:90px;
}
.navBox a, .navBox span {
    float:left;
    margin-top:0px;
    margin-right:5px;
}
.navBox span {
    float:none;
    margin-top:0px;
    margin-right:6.8px;
    margin-left:6.8px;
}
.navBox .in{padding-right:12px;}
.navBox .it{padding-right:12px;}
.navBox .tjy {padding-right: 14px;}
.navthreen {
    width: 760px;
    height: auto;
    float: left;
    margin-left: 5px;
}
.top_listone {
    width: 970px;
    height:auto;
    background:#f3f3f3;
    float: right;
    margin-left: 0;
}
.navrightjb {
    width: 200px;
    height: auto;
    float: right;
}
.w300 {width: 290px;margin-top: 10px;}
.search {
    width: 20%;
}

.search .search-name {
    float: left;
    display: block;
    font-size: 14px;
    line-height: 30px;
    color: #083b90;
}

.search .search-box {
    float: none;
    width: 100%;
    height: 28px;
    padding-left: 12px;
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
    -webkit-border-radius: 15px;
    -moz-border-radius: 15px;
    border-radius: 15px;
    border: none;
    background: #fff;
    box-sizing: border-box;
}

.search .search-box .search-input {
    display: block;
    float: left;
    line-height: 26px;
    width: 150px;
    height: 26px;
    font-size: 14px;
    outline: 0;
    border: 0;
    color: #8d9fab;
}

.search .search-box .search-btn {
    float: right;
    width: 55px;
    height: 28px;
    -webkit-border-radius: 15px;
    -moz-border-radius: 15px;
    border-radius: 15px;
    background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTM4IDc5LjE1OTgyNCwgMjAxNi8wOS8xNC0wMTowOTowMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTcgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkUzNDJDMTUzQzFFQjExRUJBODk4RkQ5MTlBMzBDMUVBIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkUzNDJDMTU0QzFFQjExRUJBODk4RkQ5MTlBMzBDMUVBIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6RTM0MkMxNTFDMUVCMTFFQkE4OThGRDkxOUEzMEMxRUEiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6RTM0MkMxNTJDMUVCMTFFQkE4OThGRDkxOUEzMEMxRUEiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz71eop8AAABsElEQVR42mL8//8/Aww8ePjY8fDhk7UgGiYmLS1x0trKrF1dTXkjAxJghGncsXP/5NNnLuSA2Jqaqmv4+fgeff78Rfra9VuhQDVM2lrqK4MCvSLgOkEat27bM72ppe///gNHm0B8dHzk6MlKkPzylRs2w8QYnj59bgYS3LvvSBs2TQjNpypA6q5euxkG4jMBbZvJyMj4z8nRuooBD7C2Mu1gY2P7vG373ukgPtOLl68NNDVU1zAQAXR1NZd8//5D6MePnwJMIAEREaHrxGgUEuS/A6K/fPkqCdb4EmgrMRrfvHmnBaK5ubleMklIiJ2/eeuuPzEar1y9GcHOzvaJk5PjHZOnh1M2SBAUSPg07dl7uOv379/cnh7OWSA+i4y05HEjQ93Z585fTgMlCBdnuxKQqTANIMV79x9pP336Qi6Iz8vL/Qwl5QBtnAXUnApiy8pKH+Hn4330+csXqYcPnzgg28zBwf4hKyNBgxE5rd6799Dt6PHT5Q8ePHZCpFXJEzbWZm2g5AeLQ2FhwZsoGpHT8I8fPwSAEf6FiYnpN0wQmMostu3YN+3Dh08KAAEGAMAv85XozbtPAAAAAElFTkSuQmCC) center center no-repeat;
    cursor: pointer;
}
.search_icon1{background:url(/channel-home/nen/images/w40.png) no-repeat left center;padding:0 0 0 20px;margin:0 0 0 10px;}
.search_icon2{color: #ff0000;background:url(/channel-home/nen/images/w41.png) no-repeat left center;padding:0 0 0 20px;margin:0 0 0 10px;}
.gsgg {color: #ff0000;background:url(/channel-home/nen/images/w47.png) no-repeat left center;padding:0 0 0 20px;margin:0;}

.left {
    float: left;
}
.right {
    float: right;
}
.clearfix {
    display: block;
}
.weather {
    width: 80px;
    height: 26px;
    line-height: 26px;
    margin: 0 10px;
    text-align: center;
}
.emall {
    margin-left: 40px;
    width: 30px;
    height: 30px;
    float: left;
    border: 0;
}
.emall img {
    border: 0;
}
.telephone {
    width: 150px;
    height: 30px;
    float: left;
    margin-left: 20px;
}
.logow {width:auto;}
.logow img {width:auto;}


		</style>
	</head>
	<body>
<div class="ph-bd-top">
<div class="logoh">
    <div class="clearfix">
						<div class="tb_text left"><p style="width:100px;float:left;margin:0px"><span id="localtime"></span></p><a href="http://www.nen.com.cn/channel-home/tgyx/tg.shtml" class="search_icon2">投稿邮箱</a></div>
						<div class="tb_text left" style="padding:0 0 0 30px;">
                                                    <span style="display:inline-block;">新闻热线 024-23187042</span> 
                                                    <span style="display:inline-block; padding-left:6px;">值班电话 024-23186204</span>
                                                </div>
                                                <div class="tb_text left" style="padding:0 0 0 30px;">
                                                    <span style="display:inline-block;"><a href="http://gsgg.nen.com.cn" target="_blank" class="gsgg">公示公告频道招商：</a>  024-23186593</span>
                                                </div>
						<div class="search right clearfix searchPos ">
							<div class="clearfix form search-box" id="f1">
								<input class="search-input" id="inputwd" type="text"
								onmouseoff="this.className='input_off'" autocomplete="off" maxlength="255"
								value="" name="wd" placeholder="搜索" data-inputcolor="#9c9c9c" />
								<a href="/channel-home/search/search.shtml"><div class="search-btn" id="searchSubmit" type="submit" name="btn" value=""></div></a>
							</div>
						</div>
					</div>
</div>
</div>
<div class="ph-bd">
			<!--顶部导航-->
			<div class="logoh">
			  <div class="logow">
                                
                                <div style="float:left;"><a href="http://www.nen.com.cn/"><img src="/channel-home/nen/images/w37nen.png" alt="东北新闻网" /></a></div>
                            <div style="float:left;"><a href="http://www.nen.com.cn/channel-home/bdrm/bdrm.shtml" target="_blank"><img src="/channel-home/nen/images/w37bd.png" alt="北斗融媒" /></a></div>
                          </div>
			  <div class="top_listone">
			  <div class="navthreen fwryh">
				<div class="navBox">
			    	    <a href="http://liaoning.nen.com.cn" target="_blank">辽宁</a>
                                    <a href="http://review.nen.com.cn" target="_blank">北斗时评</a>
                                    <a href="http://ms.nen.com.cn" target="_blank"><span style="float:none;margin:0;letter-spacing:4px;margin-left:4px;">民生帮</span></a>
                                    <a href="http://zt.nen.com.cn/" target="_blank">专题</a>
                                    <a href="http://health.nen.com.cn/" target="_blank">健康</a>
                                    <a href="http://finance.nen.com.cn" target="_blank">财经</a>
                                    <a href="http://job.nen.com.cn/" target="_blank">人才</a>
                                    <a href="http://piyao.nen.com.cn/" target="_blank">辟谣</a>
                                    <a href="http://wmln.nen.com.cn" target="_blank">文明辽宁</a>
    			    </div>
                                <div class="navBox">
                                    <a href="http://news.nen.com.cn" target="_blank">新闻</a>
                                    <a href="http://video.nen.com.cn/" target="_blank">融<span>·</span>视频</a>
                                    <a href="http://xiaofei.nen.com.cn" target="_blank">消费维权</a>
                                    <a href="http://nongye.nen.com.cn/" target="_blank">农业</a>
                                    <a href="http://liaoning.nen.com.cn/network/liaoningnews/lnnewskejiao/list/indexHome.shtml" target="_blank">科技</a>
                                    <a href="http://edu.nen.com.cn/" target="_blank" style="flex-basis: 62px;">教育</a>
                                    <a href="http://zfcg.nen.com.cn/" target="_blank" style="flex-basis: 141px;">政府采购/拍卖</a>
                                    <a href="http://gsgg.nen.com.cn/" target="_blank" style="flex-basis: 90px;">公示公告</a>
    			    </div>
			  </div>
                          <div class="navrightjb">

					

					<div class="clearfix phoneNone" style="float:right;"><a href="http://piyao.nen.com.cn/" target="_blank"><img src="/channel-home/nen/images/w38-syr-2.jpg"></a></div>
				</div>
			</div>
			</div>
			<!--顶部导航结束-->
			</div>
	</body>
<script type="text/javascript">
function showLocale(objD){
	var str,colorhead,colorfoot;
	var yy = objD.getYear();
	if(yy<1900) yy = yy+1900;
	var MM = objD.getMonth()+1;
	if(MM<10) MM = '0' + MM;
	var dd = objD.getDate();
	if(dd<10) dd = '0' + dd;
	var hh = objD.getHours();
	if(hh<10) hh = '0' + hh;
	var mm = objD.getMinutes();
	if(mm<10) mm = '0' + mm;
	var ss = objD.getSeconds();
	if(ss<10) ss = '0' + ss;
	var ww = objD.getDay();
	if  ( ww==0 )  colorhead="<font color=\"#000000\">";
	if  ( ww > 0 && ww < 6 )  colorhead="<font color=\"#000000\">";
	if  ( ww==6 )  colorhead="<font color=\"#000000\">";
	if  (ww==0)  ww="星期日";
	if  (ww==1)  ww="星期一";
	if  (ww==2)  ww="星期二";
	if  (ww==3)  ww="星期三";
	if  (ww==4)  ww="星期四";
	if  (ww==5)  ww="星期五";
	if  (ww==6)  ww="星期六";
	colorfoot="</font>"
	str = colorhead + yy + "." + MM + "." + dd + " " + colorfoot;
	return(str);
}

function tick(){
	var today;
	today = new Date();
	document.getElementById("localtime").innerHTML = showLocale(today);
	window.setTimeout("tick()", 1000);
}

tick();

</script>
</html>

			
		
		
		
            <div class="t_fbh_st_bg">
            <div class="w1280 t_fbh_st">
               您当前的位置 ：<a href='http://www.nen.com.cn'>东北新闻网</a>>><a href='http://video.nen.com.cn/network/nenvideo/index.shtml'>融 · 视频</a>>><a href='http://video.nen.com.cn/network/nenvideo/nenbenwangyc/index.shtml'>本网原创</a>
            </div>
        </div>
        
        <div class="w1280 xwzw_nr">
<div>
<div class="xwzw_l">
            <div class="list_h">
         <div class="xwzw_title">聚力攻坚 | 全省固定资产投资 实现量的合理增长和质的有效提升</div>
          <h2></h2>
         <h3></h3>
         <div class="xwzw_t1">
            <span class="fontSize">2024-10-22 21:54:01</span>
            <span class="fontSize">来源：东北新闻网</span>
            <span class="sharewx" style="position:relative;">
                    分享到:<img src="/channel-home/nen/images/weixin.png" id="share">
                    <input type="hidden" id="url" value="" />
                    <div id="qrcode" style="display: none;">
			<span style="font-size: 12px;text-align: center;">
				用微信扫码二维码<br/>
				分享至好友和朋友圈
			</span>
		    </div>
                </span>
        </div>
        </div>
        
		
            
                <div class="xwzw_t2">
                    
                    <p>
                        <p style="text-align: center;"><iframe class="ismedia mediafrom__f72c5f299e8e42eaa72b16ff6666ee16__202410__https://vodshmirror.lnyun.com.cn/a063ddc1908071efab690675b3ed0102/e8b5c9309203b2fc44e91e39cb28820d-sd.mp4" frameborder="no" allowfullscreen="true" src="https://nen.bdy.lnyun.com.cn/pages/article/view-or.html?video=f72c5f299e8e42eaa72b16ff6666ee16&divcol=202410&cover=1&q=undefined" width="700px" height="400px"></iframe></p><p>　　总监制/王雪冬</p><p>　　监制/李莹 孟曦</p><p>　　审核/赫鑫</p><p><br/></p>
                    </p>
					<div style="text-align:right;">责任编辑：张雁北</div>
                </div>

                <div class="list">
                    
                    <ul>
                     </ul>
                </div>

                <div class="erweima" style="width:100%;margin:80px auto -40px auto;float:none;overflow:hidden;">
			<div style="width:50%;float:left;">
                            <p><img src="/channel-home/nen/images/w15.jpg"></p>
                            <p>东北新闻网微博</p>
                        </div>
			<div style="width:50%;float:left;">
                            <p><img src="/channel-home/nen/images/w16.jpg"></p>
                            <p>北斗融媒</p>
                        </div>
		</div>
                <div class="xwzw_t3">
                    <p>*本网站有关内容转载自合法授权网站，如果您认为转载内容侵犯了您的权益，<br>
                       请您来信来电(024-23187042)声明，本网站将在收到信息核实后24小时内删除相关内容。
                       </p>
               </div>
</div>
<div class="xwzw_r">
                                <a href="http://ms.nen.com.cn/" target="_blank" class="xwzw_r_ad"><img src="/channel-home/nen/images/banner10.jpg?v=1"></a>
                                <a href="http://xiaofei.nen.com.cn/" target="_blank" class="xwzw_r_ad"><img src="/channel-home/nen/images/banner11.jpg?v=1"></a>
				<div class="xwzw_r_news">
				    <div class="xwzw_r_title"><img src="static/images/x10.png"  alt="" />热点推荐</div>
					<ul class="xwzw_r_list">
                                               <li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/27/705091445031179944.shtml">岁月如歌 四季长虹</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/27/705062125642454696.shtml">北斗瞰辽宁：何以文明 寻根牛河粱</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/26/705182250039252709.shtml">全省科技大会｜王学来：打造重大技术创新策源地 建设科技强省</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/26/705181496331211668.shtml">全省科技大会｜原驰：加快科技成果转化 发力战略性新兴产业</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/26/705180043290088340.shtml">全省科技大会｜胡旺阳：加强科技创新 引领产业创新</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/26/705177390875154002.shtml">全省科技大会｜金卫东：推动创新链产业链相结合</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/26/704755213885510548.shtml">“清华校友辽宁行”推介会在沈阳举行</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/26/704675192378496594.shtml">全省科技大会今日召开</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/25/704461020000687467.shtml">与会者说｜大力推动中俄地方投资合作 </a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/25/704362474685600430.shtml">深化地方合作 推动辽宁向北开放</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/25/704320511022208599.shtml">快讯｜第二届中俄地方投资发展与贸易合作大会开幕</a>
</li>
<li>
<a href="http://video.nen.com.cn/network/nenvideo/nenbenwangyc/2024/10/25/704448051468570708.shtml">倒计时1天！辽宁省科技大会即将开幕</a>
</li>

					</ul>	
				</div>
			    
			</div>
                <div class="cb"></div>
</div>            
        </div>
		<div class="ct">
			 <!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<meta name="apple-mobile-web-app-capable" content="yes">
		<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
              
                <meta http-equiv="pragma" content="no-cache">
                <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
                <meta http-equiv="expires" content="0">
		<title>${channel_name!""}</title>
		<meta name="keywords" content="东北新闻网">
		<meta itemprop="name" content="东北新闻网">
		<style type="text/css">
			
			/**************** footer *************/
			.footer {
    width: 1280px;
    margin: 0 auto;
    border-top: none;
    clear: both;
    overflow: hidden;
}
			/* fNav */
			.fNav_Box {
				width:1200px;
				margin:15px auto 10px;
				border-bottom:1px dashed #ccc;
				clear:both;
				overflow:hidden;
			}
			.fNav, .fNav_info {
				float:left;
				_display:inline;
				width:150px;
				height:75px;
				margin-left:14px;
				margin-bottom:15px;
				font-size:12px;
				padding:10px 0;
			}
			.fNav {
				line-height:25px;
				background:#E8E8E8;
			}
			.fNav:hover {
				background:#033266;
				color:#fff;
			}
			.fNav:hover a{
				color:#fff;
			}
			.fNav strong {
				display:block;
				margin:0 0 0 15px;
			}
			.fNav strong a {
				width:auto;
				margin-left:0;
			}
			.fNav a {
				display:inline-block;
				width:52px;
				margin-left:15px;
				white-space:nowrap;
			}
			.fLinks {
				margin:0 auto 10px;
				clear:both;
				overflow:hidden;
				padding-bottom:10px;
				font-size:14px;
			}
			.fLinks h3 {
				width:100%;
				height:30px;
				font-size:16px;
				font-weight:bold;
				color: #2e5389;
				
			}
			.fLinks a {
				margin-right:13px;
			        line-height: 30px;
			}
			.info {
				border-bottom:1px dashed #ccc;
				padding:15px 0;
			}
			.fnav {text-align:center;}
			.crBox {
				width:100%;
				height:25px;
				line-height:25px;
				background:#303030;
			}
			.cR {
				width:1000px;
				height:25px;
				line-height:25px;
				color:#fff;
				text-align:center;
				margin:0 auto;
			}
			.focus {
				width:320px; 
				height:220px; 
				margin-bottom:10px;
			}
			/*底部*/
			.footernew{color:#515151;font-size:12px;margin: 30px auto;overflow:hidden;text-align:center;}
			.footheight{width:80%;display: flex;
    overflow: hidden;
    align-items: center;
    justify-content: space-around;}
.fnav a {padding:0 5px; font-size:14px;}
			.footernew a{color:#515151;text-decoration:none;}
			.footernew a.lchot{color:#BD0A01;}
			.footernew a:hover{color:#BD0A01;text-decoration:underline;}
			.footernew a:visited{color:#515151;}
			.footernew div{margin:0 auto;}
			.footernew p{width:170px;border:1px solid #D2D2D2;float:left;font-size:12px;margin:6px;padding:0;text-align:center;overflow:hidden;}
			.footernew .fl{width:24%;float:left;padding:10px 0 0 0;}
                        .footernew p:nth-of-type(6) .fl{padding:5px 0 0 0;}
			.footernew .fr{width:74%;float:right;padding:5px 0px 0 0;}
.footernew .fr .lcblack{line-height:40px;}
.footernew p:nth-of-type(1) img,.footernew p:nth-of-type(2) img,.footernew p:nth-of-type(3) img {width: 100%;height: 100%;}
.footernew p:nth-of-type(4) img,.footernew p:nth-of-type(5) img {width: 80%;}
.footernew p:nth-of-type(6) img {width: 70%;}
	



		
		@media screen and (max-device-width :960px)  {
html {font-size: calc(100vw / 18.75);}
.footer {
    width: 100%;
}
.footernew p {width:49%;height:2rem;font-size:0.6rem;margin:0.1rem 0;line-height: 1rem;}
    .footernew .fl{width:25%; padding:0; margin-left:0.2rem;}

    .footernew p:nth-of-type(1) img,.footernew p:nth-of-type(2) img,.footernew p:nth-of-type(3) img {width:100%;height:100%;}
    .footernew p:nth-of-type(4) img,.footernew p:nth-of-type(5) img {width:60%;}
    .footernew p:nth-of-type(6) img {width:50%;}
    .footernew p:nth-of-type(4) .fl{margin-top:0.2rem;}
    .footernew p:nth-of-type(5) .fl{margin-top:0.2rem;}
    .footernew p:nth-of-type(6) .fl{margin-top:0rem;}
    .footernew .fr{padding:0;margin-top:0rem;margin-right:0.2rem;}
    .footernew .fr .lcblack{line-height:2rem;}
    .footernew p:nth-of-type(4) .fr{width: 67%;margin-top:0rem;}
    .footernew p:nth-of-type(5) .fr{width: 60%;margin-top:0rem;margin-right:0.6rem;}
    .footernew p:nth-of-type(6) .fr{width: 60%;margin-top:0rem;margin-right:0.6rem;}
    .footheight{width: 98%;display: flex;flex-wrap: wrap;overflow: hidden;align-items: center;justify-content: space-around;}


}
	
		</style>
	</head>
	<body>
			<!-- footer -->
			<div class="footer">
<div class="fbg">
			<div class="info fnav" style="text-align:center;background: none !important;">
<a href="http://www.nen.com.cn/channel-home/gywm/gywm.shtml" target="_blank">关于我们</a>
<a href="http://www.nen.com.cn/channel-home/tgyx/tg.shtml" target="_blank">投稿邮箱</a>
<a href="http://www.nen.com.cn/channel-home/ggbj/ggbj.shtml" target="_blank">广告报价</a>
<a href="http://www.nen.com.cn/channel-home/lianxiwomen/lianxi.shtml" target="_blank">联系我们</a>

			</div>
<div class="fnav" style="background: none !important;">—  辽宁北斗云数字科技技术支持  —</div>
			<div class="fnav" style="background: none !important;">
<span class="spanBlock "><a href="https://beian.miit.gov.cn/" target="_blank">辽ICP备2021005258号-1</a></span>
<!-- <span class="spanBlock ">增值电信业务经营许可证</span> --> 
<!-- <span class="spanBlock ">辽B1.B2-20150111 </span> --> 
<span class="spanBlock ">互联网新闻信息服务许可证</span>
<span class="spanBlock ">21120170001</span>
<span class="spanBlock ">信息网络传播视听节目许可证 0603017</span>
<p style="text-align:center;margin:0 10px;">东北新闻网(www.nen.com.cn)版权所有，未经授权禁止复制或建立镜像</p>
</div>
<div class="cb"></div>
</div>
			<div class="footernew footheight">
                                        <p>
                                                <a href="https://www.12377.cn/" target="_blank"><img src="/channel-home/nen/images/w30.jpg?v=20210906" alt="" /></a>
                                        </p>
                                        <p>
                                                <a href="https://www.lnjubao.cn/" target="_blank"><img src="/channel-home/nen/images/w30-1.jpg" alt="" /></a>
                                        </p>
				        <p>
					<a href="http://www.12377.cn/node_548446.htm" target="_blank">
						<img border="0" alt="举报专区" src="/channel-home/nen/images/newjubao20150205.jpg"></a>
					</p>
					<p>
						<span class="fl"><img border="0" alt="辽公网安备21010202000026号" src="/channel-home/nen/images/jd.gif"></span>
						<span class="fr"><a href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=21010202000026" target="_blank">辽公网安备<br>21010202000026号</a></span>
					</p>
					<p>
						<span class="fl"><img border="0" alt="沈网警备案20040314号" src="/channel-home/nen/images/jd.gif"></span>
						<span class="fr">沈网警备案<br>20040314号</span>
					</p>
					<p>
						<span class="fl"><a href="http://ln.cyberpolice.cn/alertPawsAction.do?method=LOUT" target="_blank"><img border="0" alt="辽宁网警" src="/channel-home/nen/images/sywj.gif"></a></span>
						<span class="fr"><a class="lcblack" href="http://ln.cyberpolice.cn/alertPawsAction.do?method=LOUT" target="_blank" rel="nofollow">辽宁网警</a></span>
					</p>
				</div>
			</div>
			<!-- footer end --> 
	
	</body>
</html>

		</div>
        <script src="/channel-home/nen/js/jquery.min.js"></script>
	<script src="/channel-home/nen/js/qrcode.js"></script>
<script src="/channel-home/nen/js/nrimg.js?v=1.0.3"></script>
	<script type="text/javascript">
		$(function(){
                        $('iframe').attr('scrolling','no');
			$('#url').val(window.location.href);
			
			var qrcode = new QRCode("qrcode");
			// 生成二维码的方法
			function makeCode () {
				// 二维码地址 
				var Url = document.getElementById("url");
				if (!Url.value) {
					alert("请输入生成二维码的地址");
					Url.focus();
					return;
				}
				qrcode.makeCode(Url.value);
			}
			makeCode();
			
			$('#share').on('click',function(){
				let temp = $('#qrcode').css('display');
				if(temp=='block') {$('#qrcode').hide()};
				if(temp=='none') {$('#qrcode').show()};
			});
		});
	</script>
	</body>
</html>


"""


def is_likely_header_or_footer(element):
    """
    判断一个元素是否可能是header或footer
    """
    # 检查标签名和class/id
    if element.name in ['header', 'footer', 'nav']:
        return True
    
    suspicious_terms = [
        'header', 'footer', 'navigation', 'nav', 'menu', 'banner', 
        'copyright', 'logo', 'social', 'sidebar', 'widget', 'breadcrumb',
        'pagination', 'comment', 'advertisement', 'ad-', '-ad', 'share'
    ]
    
    # 检查class和id中的关键词
    element_classes = ' '.join(element.get('class', [])).lower() if element.get('class') else ''
    element_id = element.get('id', '').lower()
    
    return any(term in element_classes or term in element_id for term in suspicious_terms)

def is_likely_noise(element):
    """
    检查是否是干扰元素
    """
    noise_tags = {
        'script', 'style', 'iframe', 'noscript', 'option', 'button',
        'form', 'input', 'textarea', 'select', 'svg', 'canvas'
    }
    return element.name in noise_tags

def is_content_tag(tag):
    """
    检查是否是可能包含内容的标签
    """
    content_tags = {
        # 文本容器
        'p', 'div', 'span', 'article', 'section', 'main',
        # 标题
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        # 列表
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        # 表格
        'table', 'tr', 'td', 'th',
        # 其他文本元素
        'blockquote', 'pre', 'code', 'em', 'strong', 'small',
        'figure', 'figcaption', 'caption',
        # 文本格式化
        'b', 'i', 'u', 'mark', 'cite', 'q',
        # 自定义文本容器
        'text', 'content', 'paragraph'
    }
    return tag.name in content_tags

def has_meaningful_text(element, min_length=10):
    """
    检查元素是否包含有意义的文本
    排除纯空格、纯符号等无意义内容
    """
    text = element.get_text(strip=True)
    if not text or len(text) < min_length:
        return False
        
    # 检查是否全是特殊字符
    special_chars = set(',.!?;:()[]{}|/\\<>+=_-*&^%$#@~`"\'')
    text_chars = set(text)
    if all(char in special_chars for char in text_chars):
        return False
        
    # 检查是否是常见的噪音文本
    noise_patterns = [
        r'^[0-9\W]+$',  # 纯数字或特殊字符
        r'^(powered by|copyright|\(c\)|©|all rights reserved)',  # 版权信息
        r'^(share|like|follow|subscribe|sign up|login|register)',  # 行动号召
        r'^(previous|next|page|[0-9]+ of [0-9]+)',  # 导航元素
    ]
    
    return not any(re.match(pattern, text.lower()) for pattern in noise_patterns)


soup = BeautifulSoup(html_content, 'html.parser')

# 移除注释和无用标签
for element in soup.find_all(string=lambda text: isinstance(text, Comment)):
    element.extract()

for element in soup.find_all(is_likely_noise):
    element.decompose()

# 移除header和footer
for element in soup.find_all(is_likely_header_or_footer):
      element.decompose()

page_date = find_date(html_content, outputformat='%Y-%m-%d %H:%M:%S')
print(page_date)
import json
from trafilatura import extract
options = Extractor(output_format="json", with_metadata=True)
options.formatting = True

page_text = extract(html_content, options=options)
json_data = json.loads(page_text)
print(json_data)
# print(page_text.raw_text)
# print(json_data['title'])
# print(json_data['raw_text'])


