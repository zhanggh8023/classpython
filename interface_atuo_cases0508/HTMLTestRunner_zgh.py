# coding=utf-8

"""
Change History
Version 1.2.0.0 -zhanggh
*新增数据库存储测试记录方法
*修正百分比占比

Version 1.1.0.0 -zhanggh
*新增历史十次的测试结果展示
*修改excel读取写入方法
*添加错误率百分比

Version 1.0.0.0 -zhanggh
*新增报表格式
*添加饼状图显示百分比
*新增判断成功、错误、失败、所有、概要独立显示
*预留最近10天结果存储方法

Version 0.8.2.1
* 支持中文，汉化
* 调整样式，美化（需要连入网络，使用的百度的Bootstrap.js）
* 增加 通过分类显示、测试人员、通过率的展示
* 优化“详细”与“收起”状态的变换
* 增加返回顶部的锚点
Version 0.8.2
* Show output inline instead of popup window (Viorel Lupu).
Version in 0.8.1
* Validated XHTML (Wolfgang Borgert).
* Added description of test classes and test cases.
Version in 0.8.0

* Define Template_mixin class for customization.
* Workaround a IE 6 bug that it does not treat <script> block as CDATA.
Version in 0.7.1
* Back port to Python 2.3 (Frank Horowitz).
* Fix missing scroll bars in detail log (Podi).
"""
__author__ = "zhanggh"
__version__ = "1.0.0.0"

# TODO: color stderr
# TODO: simplify javascript using ,ore than 1 class in the class attribute?

import io
import datetime
import sys
import time
from conf import Allpath
from public.get_mysql_info import getMysqlInfo
from public.all_method import projectenv
import unittest
from xml.sax import saxutils
from public.logger import Log

logger = Log('HTMLTestRunner', Allpath.log_path)

gmi = getMysqlInfo(projectenv[2])

PY3K = (sys.version_info[0] > 2)
if PY3K:
    import io as StringIO
else:
    import StringIO
import copy


# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing. Output
# sent to sys.stdout and sys.stderr are automatically captured. However
# in some cases sys.stdout is already cached before HTMLTestRunner is
# invoked (e.g. calling logging.basicConfig). In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.
#   >>> logging.basicConfig(stream=HTMLTestRunner.stdout_redirector)
#   >>>

class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)


# ----------------------------------------------------------------------
# Template

class Template_mixin(object):
    """
    Define a HTML template for report customerization and generation.
    Overall structure of an HTML report
    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {
        0: '通过',
        1: '失败',
        2: '错误',
    }

    DEFAULT_TITLE = 'Python接口自动化测试报告'
    DEFAULT_DESCRIPTION = ''
    DEFAULT_TESTER = '咘啾'

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    %(stylesheet)s
    <link href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css" rel="stylesheet">
    <script src="http://libs.baidu.com/jquery/2.0.0/jquery.min.js"></script>
    <script src="http://libs.baidu.com/bootstrap/3.0.3/js/bootstrap.min.js"></script>
    <script src="https://cdn.bootcss.com/echarts/3.8.5/echarts.common.min.js"></script>
</head>
<body>
    <script language="javascript" type="text/javascript">
    output_list = Array();
/*level 调整增加只显示通过用例的分类
0:Summary //all hiddenRow
1:Failed  //pt hiddenRow, ft none
2:Pass    //pt none, ft hiddenRow
3:All     //pt none, ft none
4:Error  
*/
    function showCase(level) {
        trs = document.getElementsByTagName("tr");
     
        for (var i = 0; i < trs.length; i++) {
            tr = trs[i];
            id = tr.id;
            
            if (id.substr(0,2) == 'ft' || id.substr(0,2) == 'pt'){
                if (level == 0) {
                    tr.className = 'hiddenRow';
                }
                else if (level == 1) {
                    button = tr.children[1].children[0].innerText;
                    if(button == "失败"){
                        tr.className = '';
                    }else{
                        tr.className = 'hiddenRow';
                    }
                }
                else if(level == 2){
                    button = tr.children[1].children[0].innerText;
                    if(button == "通过"){
                        tr.className = '';
                    }else{
                        tr.className = 'hiddenRow';
                    }
                }
                else if(level == 3){
                    tr.className = '';
                }
                else if(level == 4){
                    button = tr.children[1].children[0].innerText;
                    if(button == "错误"){
                        tr.className = '';
                    }else{
                        tr.className = 'hiddenRow';
                    }
                }
            }
        }
        //加入【详细】切换文字变化 
        detail_class=document.getElementsByClassName('detail');
        //console.log(detail_class.length)
        if (level == 3) {
            for (var i = 0; i < detail_class.length; i++){
                detail_class[i].innerHTML="收起"
            }
        }
        else{
                for (var i = 0; i < detail_class.length; i++){
                detail_class[i].innerHTML="详细"
            }
        }
    }
    function showClassDetail(cid, count) {
        var id_list = Array(count);
        var toHide = 1;
        for (var i = 0; i < count; i++) {
            //ID修改 点 为 下划线 -Findyou
            tid0 = 't' + cid.substr(1) + '_' + (i+1);
            tid = 'f' + tid0;
            tr = document.getElementById(tid);
            if (!tr) {
                tid = 'p' + tid0;
                tr = document.getElementById(tid);
            }
            id_list[i] = tid;
            if (tr.className) {
                toHide = 0;
            }
        }
        for (var i = 0; i < count; i++) {
            tid = id_list[i];
            //修改点击无法收起的BUG，加入【详细】切换文字变化 
            if (toHide) {
                document.getElementById('div_'+tid).style.display = 'none'
                document.getElementById(tid).className = 'hiddenRow';
                document.getElementById(cid).innerText = "详细"
            }
            else {
                document.getElementById(tid).className = '';
                document.getElementById(cid).innerText = "收起"
            }
        }
    }

    function showTestDetail(div_id){
        var details_div = document.getElementById(div_id)
        var displayState = details_div.style.display
        // alert(displayState)
        if (displayState != 'block' ) {
            displayState = 'block'
            details_div.style.display = 'block'
        }
        else {
            details_div.style.display = 'none'
        }
    }
    function html_escape(s) {
        s = s.replace(/&/g,'&amp;');
        s = s.replace(/</g,'&lt;');
        s = s.replace(/>/g,'&gt;');
        return s;
    }
    </script>

    <div id="div_base">
        %(heading)s
        %(report)s
        %(ending)s
        %(chart_script)s

    </div>
</body>
</html>
"""  # variables: (title, generator, stylesheet, heading, report, ending, chart_script)

    ECHARTS_SCRIPT = """
        <script type="text/javascript">
        var myChartline = echarts.init(document.getElementById('chartline'));
        var optionline = {
            title : {
                text: '近十次情况展示',
                subtext: '成功表示：验证通过；失败表示：验证失败；错误表示：验证报错。'
            },
            color:['#06ff26','#001686','#f31616'],
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    crossStyle: {
                        color: '#999'
                    }
                }
            },
            toolbox: {
                show : true,
                feature: {
                    mark : {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            calculable : true,
            legend: {
                data:['错误','成功','失败'],
                //backgroundColor:['#d63131','#449dd4','#af29e4']
            },
            xAxis: [
                {
                    type: 'category',
                    data: ['LAST','九次','八次','七次','六次','五次','四次','三次','两次','最近'],
                    axisPointer: {
                        type: 'shadow'
                    }
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    name: '',
                    min: 0,
                    max: 1000,
                    interval: 50,
                    axisLabel: {
                        formatter: '{value}'
                    }
                },
                {
                    type: 'value',
                    name: '错误率',
                    min: 0,
                    max: 100,
                    interval: 10,
                    axisLabel: {
                        formatter: '{value}%%'
                    }
                }
            ],
            series: [
                {
                    name:'成功',
                    type:'bar',
                    //data:[%(Pass)s]
                    data:%(Pass)s
                },
                {
                    name:'失败',
                    type:'bar',
                    //data:[%(fail)s]
                    data:%(fail)s
                },
                {
                    name:'错误',
                    type:'line',
                    yAxisIndex: 1,
                    //data:[%(error)s]
                    data:%(error_1)s
                }
            ]
        };
        myChartline.setOption(optionline);
        console.log(%(fail)s,%(Pass)s,%(error)s)
            // 基于准备好的dom，初始化echarts实例
            var myChart = echarts.init(document.getElementById('chart'));

            // 指定图表的配置项和数据
            var option = {
                color:['#06ff26','#001686','#f31616'],
                title : {
                    text: '近十次测试执行情况',
                    x:'center'
                },
                tooltip : {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: ['通过','失败','错误']
                },
                series : [
                    {
                        name: '近十次测试执行情况',
                        type: 'pie',
                        radius : '60%%',
                        center: ['50%%', '60%%'],
                        data:[
                            {value:%(Pass)s, name:'通过'},
                            {value:%(fail)s, name:'失败'},
                            {value:%(error)s, name:'错误'}
                        ],
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };

            // 使用刚指定的配置项和数据显示图表。
            myChart.setOption(option);
        </script>
    """

    # variables: (Pass, fail, error)

    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">
    body        { font-family: Microsoft YaHei,Tahoma, arial, helvetica, sans-serif; font-size: 80%; }
    table       { font-size: 100%; }
    pre         { white-space: pre-wrap;word-wrap: break-word; }

    /* -- heading ---------------------------------------------------------------------- */
    h1 {
        font-size: 16pt;
        color: gray;
    }
    .heading {
        margin-top: 0ex;
        margin-bottom: 1ex;
    }

    .heading .attribute {
        margin-top: 1ex;
        margin-bottom: 0;
    }

    .heading .description {
        margin-top: 2ex;
        margin-bottom: 3ex;
    }

    /* -- css div popup ------------------------------------------------------------------------ */
    a.popup_link {
    }

    a.popup_link:hover {
        color: red;
    }

    .popup_window {
        display: none;
        position: relative;
        left: 0px;
        top: 0px;
        /*border: solid #627173 1px; */
        padding: 10px;
        /* */
        font-family: "Lucida Console", "Courier New", Courier, monospace;
        text-align: left;
        font-size: 8pt;
        /* width: 500px;*/
    }

    }
    /* -- report ------------------------------------------------------------------------ */
    #show_detail_line {
        margin-top: 3ex;
        margin-bottom: 1ex;
    }
    #result_table {
        width: 99%;
    }
    #header_row {
        font-weight: bold;
        color: #303641;

    }
    #total_row  { font-weight: bold; }
    .passClass  {  }
    .failClass  { background-color: #ffefa4; }
    .errorClass {  }
    .passCase   { color: #6c6; }
    .failCase   { color: #FF6600; font-weight: bold; }
    .errorCase  { color: #c00; font-weight: bold; }
    .hiddenRow  { display: none; }
    .testcase   { margin-left: 2em; }


    /* -- ending ---------------------------------------------------------------------- */
    #ending {
    }

    #div_base {
                position:absolute;
                top:0%;
                left:5%;
                right:5%;
                width: auto;
                height: auto;
                margin: -15px 0 0 0;
    }
</style>
"""

    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """
    <div class='page-header'>
        <h1>%(title)s</h1>
    %(parameters)s
    <div style="float: left;width:50%%;"><p class='description'>%(description)s</p></div>
    </div>
    <div id="chartline" style="width:50%%;height:400px;float:left;"></div>
    <div id="chart"style="width:50%%;height:400px;float:right;"></div>
"""  # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s:</strong> %(value)s</p>
"""  # variables: (name, value)

    # ------------------------------------------------------------------------
    # Report
    #
    # 汉化,加美化效果
    REPORT_TMPL = """
    <div class="btn-group btn-group-sm">
         <!-- <button class="btn btn-default" onclick='javascript:showCase(0)'>总结</button> -->
        <!--<button class="btn btn-default" onclick='javascript:showCase(1)'>失败</button>-->
        <!--<button class="btn btn-default" onclick='javascript:showCase(2)'>全部</button>-->
        <a class="btn btn-primary" onclick='javascript:showCase(0)'>概要 %(passrate)s </a>
        <a class="btn btn-success" onclick='javascript:showCase(2)'>通过 %(Pass)s </a>
        <a class="btn btn-warning" onclick='javascript:showCase(1)'>失败  %(fail)s </a>
        <a class="btn btn-danger" onclick='javascript:showCase(4)'>错误 %(error)s </a>  
        <a class="btn btn-info" onclick='javascript:showCase(3)'>所有 %(count)s </a>
    </div>
    <p></p>
    <table id='result_table' class="table table-condensed table-bordered table-hover">
        <colgroup>
            <col align='left' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
        </colgroup>
    <tr id='header_row' class="text-center success" style="font-weight: bold;font-size: 16px;">
        <td>用例集/测试用例</td>
        <td>总计</td>
        <td>通过</td>
        <td>失败</td>
        <td>错误</td>
        <td>详细</td>
        <td>截图</td>
    </tr>
    %(test_list)s
    <tr id='total_row' class="text-center active">
        <td>总计</td>
        <td>%(count)s</td>
        <td>%(Pass)s</td>
        <td>%(fail)s</td>
        <td>%(error)s</td>
        <td>通过率：%(passrate)s</td>
        <td> <a href="" target="_blank"></a></td>
    </tr>
    </table>
    """  # variables: (test_list, count, Pass, fail, error ,passrate)

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s warning'>
    <td>%(desc)s</td>
    <td class="text-center">%(count)s</td>
    <td class="text-center">%(Pass)s</td>
    <td class="text-center">%(fail)s</td>
    <td class="text-center">%(error)s</td>
    <td class="text-center"><a href="javascript:showClassDetail('%(cid)s',%(count)s)" class="detail" id='%(cid)s'>详细</a></td>
    <td class="text-center">Assert or Error Image</td>
</tr>
"""  # variables: (style, desc, count, Pass, fail, error, cid)

    # 失败 的样式，去掉原来JS效果，美化展示效果  -Findyou
    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s' width='300px'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='left' width='600px'> <!--print 输出框位置-->
    <!--默认收起错误信息  -->
    <button id='btn_%(tid)s' type="button"  class="btn btn-danger btn-xs collapsed" data-toggle="collapse" data-target='#div_%(tid)s'>%(status)s</button>
    <div id='div_%(tid)s' class="collapse"> 
    <!-- 默认展开错误信息  
    <button id='btn_%(tid)s' type="button"  class="btn btn-danger btn-xs" data-toggle="collapse" data-target='#div_%(tid)s'>%(status)s</button>
    <div id='div_%(tid)s' class="collapse in">-->
    <pre style="overflow-y:scroll; overflow-x:hidden;height:200px; width:auto; margin:auto; border:1px solid #e1e1e1;">
    %(script)s
    </pre>
    </div>
    </td>
    <td align="right">
        <a %(hidde)s href="%(image)s">
            <img   src="%(image)s" height="200px" width="400px"/>
        </a>
    </td>
</tr>


"""  # variables: (tid, Class, style, desc, status)

    # 通过 的样式，加标签效果  -Findyou
    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'><span class="label label-success success">%(status)s</span></td>
    <td align="right">
        <a %(hidde)s href="%(image)s">
            <img   src="%(image)s" height="200" width="400"/>
        </a>
    </td>
</tr>
"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_OUTPUT_TMPL = r"""%(id)s: %(output)s"""  # variables: (id, output)
    IMG_TMPL = r"""
            <a href="#"  onclick="show_img(this)">显示截图</a>
        <div align="center" class="screenshots"  style="display:none;z-index:2000">
            <a class="close_shots"  href="#"   onclick="hide_img(this)"></a>
            %(imgs)s
            <div class="imgyuan"></div>
        </div>
        """
    # ------------------------------------------------------------------------
    # ENDING
    #
    # 增加返回顶部按钮
    ENDING_TMPL = """<div id='ending'>&nbsp;</div>
    <div style=" position:fixed;right:50px; bottom:30px; width:20px; height:20px;cursor:pointer">
    <a href="#"><span class="glyphicon glyphicon-eject" style = "font-size:30px;" aria-hidden="true">
    </span></a></div>
    """

    # -------------------- The end of the Template class -------------------
    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if PY3K:
            return value
        else:
            if isinstance(value, str):
                return value.decode("utf-8")
            else:
                return value


TestResult = unittest.TestResult


class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.

    def __init__(self, verbosity=1):
        TestResult.__init__(self)
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []
        self.subtestlist = []
        # 增加一个测试通过率
        self.passrate = float(0)

    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr
        self.outputBuffer = io.StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E列表  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E列表')

    def addFailure(self, test, err):
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')

    def addSubTest(self, test, subtest, err):
        if err is not None:
            if getattr(self, 'failfast', False):
                self.stop()
            if issubclass(err[0], test.failureException):
                self.failure_count += 1
                errors = self.failures
                errors.append((subtest, self._exc_info_to_string(err, subtest)))
                output = self.complete_output()
                self.result.append((1, test, output + '\nSubTestCase Failed:\n' + str(subtest),
                                    self._exc_info_to_string(err, subtest)))
                if self.verbosity > 1:
                    sys.stderr.write('F')
                    sys.stderr.write(str(subtest))
                    sys.stderr.write('\n')
                else:
                    sys.stderr.write('F')
            else:
                self.error_count += 1
                errors = self.errors
                errors.append((subtest, self._exc_info_to_string(err, subtest)))
                output = self.complete_output()
                self.result.append(
                    (2, test, output + '\nSubTestCase Error:\n' + str(subtest), self._exc_info_to_string(err, subtest)))
                if self.verbosity > 1:
                    sys.stderr.write('E  ')
                    sys.stderr.write(str(subtest))
                    sys.stderr.write('\n')
                else:
                    sys.stderr.write('E')
            self._mirrorOutput = True
        else:
            self.subtestlist.append(subtest)
            self.subtestlist.append(test)
            self.success_count += 1
            output = self.complete_output()
            self.result.append((0, test, output + '\nSubTestCase Pass:\n' + str(subtest), ''))
            if self.verbosity > 1:
                sys.stderr.write('ok ')
                sys.stderr.write(str(subtest))
                sys.stderr.write('\n')
            else:
                sys.stderr.write('.')


class HTMLTestRunner(Template_mixin):

    def __init__(self, stream=sys.stdout, verbosity=2, title=None, description=None, tester=None):
        self.stream = stream
        self.verbosity = verbosity
        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description
        if tester is None:
            self.tester = self.DEFAULT_TESTER
        else:
            self.tester = tester

        self.startTime = datetime.datetime.now()

    def run(self, test):
        "Run the given test case or test suite."
        result = _TestResult(self.verbosity)
        test(result)
        self.stopTime = datetime.datetime.now()
        self.generateReport(test, result)

        print(sys.stderr, '\nTime Elapsed: %s' % (self.stopTime - self.startTime), file=sys.stderr)

        return result

    def sortResult(self, result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n, t, o, e in result_list:
            cls = t.__class__
            if cls not in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, t, o, e))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    # 替换测试结果status为通过率
    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        count = {'restult':'','sum': 0, 'ok': 0, 'fail': 0, 'error': 0,'error_1':0,'date':''}
        status.append('共 %s 条接口用例' % (result.success_count + result.failure_count + result.error_count))
        count['sum'] = result.success_count + result.failure_count + result.error_count
        if result.success_count:
            status.append('通过 %s 条' % result.success_count)
            count['ok'] = result.success_count
        if result.failure_count:
            status.append('失败 %s 条' % result.failure_count)
            count['fail'] = result.failure_count
        if result.error_count:
            status.append('错误 %s 条' % result.error_count)
            count['error'] = result.error_count
            count['error_1']=str("%.2f" % (float(result.error_count) / float(result.success_count + result.failure_count + result.error_count) * 100))
        if status:
            status = '，'.join(status)
            self.passrate = str("%.2f%%" % (float(result.success_count) / float(
                result.success_count + result.failure_count + result.error_count) * 100))
        else:
            status = 'none'
        count["restult"] = str({'testname': self.tester, 'time': startTime, 'sumtime': duration, 'testresult': status,
                                'tonggl': self.passrate})
        count['date'] = time.strftime('%Y-%m-%d_%H_%M_%S')
        # print(count)
        gmi.Instert_mysql([count])

        return [
            (u'测试人员', self.tester),
            (u'开始时间', startTime),
            (u'合计耗时', duration),
            (u'本次结果', status + "，通过率= " + self.passrate),
        ]

    def generateReport(self, test, result):
        report_attrs = self.getReportAttributes(result)
        generator = 'HTMLTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        ending = self._generate_ending()
        chart = self._generate_chart(result)
        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
            chart_script=chart,
        )
        self.stream.write(output.encode('utf8'))

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    # 增加Tester显示
    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(self.title),
            parameters=''.join(a_lines),
            description=saxutils.escape(self.description),
            tester=saxutils.escape(self.tester),
        )
        return heading

    # 生成报告 添加注释
    def _generate_report(self, result):
        rows = []
        sortedResult = self.sortResult(result.result)
        for cid, (cls, cls_results) in enumerate(sortedResult):
            # subtotal for a class
            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            desc = doc and '%s: %s' % (name, doc) or name

            row = self.REPORT_CLASS_TMPL % dict(
                style=ne > 0 and 'errorClass' or nf > 0 and 'failClass' or 'passClass',
                desc=desc,
                count=np + nf + ne,
                Pass=np,
                fail=nf,
                error=ne,
                cid='c%s' % (cid + 1),
            )
            rows.append(row)

            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            # 统计全部的
            passrate=str("%.2f%%" % (float(result.success_count) /
                                     float(result.success_count + result.failure_count + result.error_count) * 100)
                         ),
        )
        return report

    def _generate_chart(self, result):
        redata = gmi.get_mysql_info_test("select * from jkgl ORDER BY date DESC LIMIT 10;", 1)
        logger.info("本次报告获取测试结果数据成功！")
        chart = self.ECHARTS_SCRIPT % dict(
            Pass=str(redata['ok']),
            fail=str(redata['fail']),
            error=str(redata['error']),
            error_1=str(redata['error_1']),
        )
        return chart

    def _generate_report_test(self, rows, cid, tid, n, t, o, e):
        # e.g. 'pt1.1', 'ft1.1', etc
        has_output = bool(o or e)
        # ID修改点为下划线,支持Bootstrap折叠展开特效
        tid = (n == 0 and 'p' or 'f') + 't%s_%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        if self.verbosity > 1:
            doc = t._testMethodDoc or ''
        else:
            doc = ""

        # doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name
        if not PY3K:
            if isinstance(desc, str):
                desc = desc.decode("utf-8")
        tmpl = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL or self.REPORT_TEST_NO_OUTPUT_TMPL

        # utf-8 支持中文 - Findyou
        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            # uo = o.decode('latin-1')
            if PY3K:
                uo = o
            else:
                uo = o.decode('utf-8', 'ignore')
        else:
            uo = o
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            # ue = e.decode('latin-1')
            if PY3K:
                ue = e
            elif e.find("Error") != -1 or e.find("Exception") != -1:
                es = e.decode('utf-8', 'ignore').split('\n')
                es[-2] = es[-2].decode('unicode_escape')
                ue = u"\n".join(es)
            else:
                ue = e.decode('utf-8', 'ignore')
        else:
            ue = e
        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            output=saxutils.escape(o + e),
        )
        if getattr(t, 'imgs', []):
            # 判断截图列表，如果有则追加
            tmp = u""
            for i, img in enumerate(t.imgs):
                if i == 0:
                    tmp += """ <img src="data:image/jpg;base64,%s" style="display: block;" class="img"/>\n""" % img
                else:
                    tmp += """ <img src="data:image/jpg;base64,%s" style="display: none;" class="img"/>\n""" % img
            imgs = self.IMG_TMPL % dict(imgs=tmp)
        else:
            imgs = u"""无截图"""
            hidde_status = '''hidden="hidden"'''
            image_url = ''

        row = tmpl % dict(
            tid=tid,
            Class=(n == 0 and 'hiddenRow' or 'none'),
            style=(n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'none')),
            desc=desc,
            script=script,
            hidde=hidde_status,
            image=image_url,
            status=self.STATUS[n],
            img=imgs,
        )
        rows.append(row)
        if not has_output:
            return

    def _generate_ending(self):
        return self.ENDING_TMPL


##############################################################################
# Facilities for running tests from the command line
##############################################################################

# Note: Reuse unittest.TestProgram to launch test. In the future we may
# build our own launcher to support more specific command line
# parameters like test title, CSS, etc.
class TestProgram(unittest.TestProgram):
    """
    A variation of the unittest.TestProgram. Please refer to the base
    class for command line parameters.
    """

    def runTests(self):
        # Pick HTMLTestRunner as the default test runner.
        # base class's testRunner parameter is not useful because it means
        # we have to instantiate HTMLTestRunner before we know self.verbosity.
        if self.testRunner is None:
            self.testRunner = HTMLTestRunner(verbosity=self.verbosity)
        unittest.TestProgram.runTests(self)


main = TestProgram

##############################################################################
# Executing this module from the command line
##############################################################################

if __name__ == "__main__":
    main(module=None)
