Sub main()
'
' 测试输入字
'

    Dim MyCtrl()
    MyCtrl = Array("热风温度", "送风风量", "热风压力", "富氧量", "喷吹速率", "鼓风动能", "块矿比例", "球团比例", "烧结比例")
    
    Dim MyProd()
    MyProd = Array("焦炭负荷", "透气性指数", "炉腹煤气发生量", "理论燃烧温度", "炉顶温度(极差)", "炉喉温度(极差)", "煤气利用率", "[铁水温度]", "[Si]+[Ti]", "[S]", "R2")
    
    'Selection.TypeText Text:=MyCtrl(1) + "1. 焦炭负荷与热风温度"
    
    Dim time()
    
    time = Array(240, 240, 240, 240, 240, 240, 360, 360, 360, _
                   0, 0, 0, 0, 0, 0, 360, 360, 360, _
                   0, 0, 2, 0, 0, 0, 240, 240, 240, _
                   61, 60, 3, 25, 86, 82, 240, 240, 240, _
                   44, 50, 51, 2, 0, 5, 240, 240, 240, _
                   159, 336, 360, 340, 250, 180, 308, 240, 240, _
                   33, 0, 4, 13, 41, 36, 253, 240, 240, _
                   360, 360, 335, 240, 360, 360, 360, 240, 360, _
                   240, 261, 316, 258, 240, 240, 360, 240, 240, _
                   240, 281, 360, 360, 360, 240, 360, 360, 360, _
                   240, 281, 297, 360, 240, 240, 240, 360, 360)

    
    Dim ctrl As String
    Dim prod As String
    Dim i As Long
    Dim j As Long
    Dim picIdx As Long
    
    For j = 0 To 10
    For i = 0 To 8
    
    'i = 0
    'j = 0
    picIdx = j * 9 + i + 1
    
    ctrl = MyCtrl(i)
    prod = MyProd(j)
    
'标题
    Selection.TypeText Text:=Str(picIdx) + ". " + prod + "与" + ctrl
    Selection.Style = ActiveDocument.Styles("小标题样式")
    Selection.TypeParagraph
' 原始变化
    Selection.TypeText Text:="(1) 原始变化曲线"
    Selection.Style = ActiveDocument.Styles("正文样式")
    Selection.TypeParagraph
    
    Selection.TypeText Text:="根据所采集的数据，" + prod + "与" + ctrl + "的原始变化曲线如图" + Str(picIdx) + ".1所示。为方便对比，对两指标参数的数值进行了标准化处理。"
    Selection.Style = ActiveDocument.Styles("正文样式")
    If (prod <> "焦炭负荷" And prod <> "[铁水温度]") Then
        Selection.TypeText Text:="另外，为了更好地体现时滞处理的效果，我们选取了某月中两天的变化趋势进行比较。"
        Selection.Style = ActiveDocument.Styles("正文样式")
    End If
    Selection.TypeParagraph
    
    
    Selection.InlineShapes.AddPicture FileName:= _
        "C:\Users\Administrator\Desktop\时间滞后分析结果v1.0\滞后\" + prod + "与" + ctrl + "的波动图(未滞后处理).png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '居中
    Selection.TypeParagraph
    
    Selection.TypeText Text:="图" + Str(picIdx) + ".1. " + prod + "与" + ctrl + "与的原始变化曲线"
    Selection.Style = ActiveDocument.Styles("图注样式")
    Selection.TypeParagraph
    
' 相关性分析曲线
    
    Selection.TypeText Text:="(2) 相关性分析曲线"
    Selection.Style = ActiveDocument.Styles("正文样式")
    Selection.TypeParagraph
    
    Selection.TypeText Text:="根据两个变量的原始变化曲线，进行相关性分析，分析结果如图" + Str(picIdx) + _
                            ".2所示，结合时间滞后范围参数设定，最终确定" + prod + "相对于" + ctrl + "的滞后时间为" + Str(time(j * 9 + i)) + "分钟。"
    Selection.Style = ActiveDocument.Styles("正文样式")
    Selection.TypeParagraph
    
    Selection.InlineShapes.AddPicture FileName:= _
        "C:\Users\Administrator\Desktop\时间滞后分析结果v1.0\滞后\" + prod + "与" + ctrl + "的滞后时间分析图.png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '居中
    Selection.TypeParagraph
    
    
    Selection.TypeText Text:="图" + Str(picIdx) + ".2. " + prod + "与" + ctrl + "的相关性分析结果曲线"
    Selection.Style = ActiveDocument.Styles("图注样式")
    Selection.TypeParagraph
    
' (3) 根据滞后时间进行处理后的曲线
    
    Selection.TypeText Text:="(3) 根据滞后时间进行处理后的曲线"
    Selection.Style = ActiveDocument.Styles("正文样式")
    Selection.TypeParagraph
    
    Selection.TypeText Text:="根据所获得的两个变量的时滞分析结果，对两个原始曲线进行调整，即将生产指标参数" + prod + "往前调整" + Str(time(j * 9 + i)) + _
                            "分钟，可以获得两个变量的对应曲线。"
    
    '，如图" + Str(picIdx) + ".3所示，从结果中可以看出，经过时滞处理后，两个曲线之间具有较好的对应关系。"
    
    Selection.Style = ActiveDocument.Styles("正文样式")
    Selection.TypeParagraph
    
    Selection.InlineShapes.AddPicture FileName:= _
        "C:\Users\Administrator\Desktop\时间滞后分析结果v1.0\滞后\" + prod + "与" + ctrl + "的波动图(滞后处理后).png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '居中
    Selection.TypeParagraph
    
    
    Selection.TypeText Text:="图" + Str(picIdx) + ".3. " + prod + "与" + ctrl + "的滞后处理曲线"
    Selection.Style = ActiveDocument.Styles("图注样式")
    Selection.TypeParagraph
    
    Next i
    Next j

End Sub
Sub 调整图大小()
'
' 宏3 宏
'
'
    Dim n '图片个数

    ' On Error Resume Next '忽略错误
    
    For n = 1 To ActiveDocument.InlineShapes.Count 'InlineShapes 类型 图片
    
    ActiveDocument.InlineShapes(n).Height = 8 * 28.35 '设置图片高度为 6cm（1cm等于28.35px）
    
    ActiveDocument.InlineShapes(n).Width = 10.67 * 28.35 '设置图片宽度 6cm
    
    Next n
    
End Sub

