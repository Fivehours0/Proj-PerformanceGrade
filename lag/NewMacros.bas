Attribute VB_Name = "NewMacros"
Sub main()
'
' ����������
'

    Dim MyCtrl()
    MyCtrl = Array("�ȷ��¶�", "�ͷ����", "�ȷ�ѹ��", "������", "�紵����", "�ķ綯��", "������", "���ű���", "�ս����")
    
    Dim MyProd()
    MyProd = Array("��̿����", "͸����ָ��", "¯��ú��������", "����ȼ���¶�", "¯���¶�(����)", "¯���¶�(����)", "ú��������", "[��ˮ�¶�]", "[Si]+[Ti]", "[S]", "R2")
    
    'Selection.TypeText Text:=MyCtrl(1) + "1. ��̿�������ȷ��¶�"
    
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
    Dim FilePath As String
    
    FilePath = Application.Path
    
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
    
'����
    Selection.TypeText Text:=Str(picIdx) + ". " + prod + "��" + ctrl
    Selection.Style = ActiveDocument.Styles("С������ʽ")
    Selection.TypeParagraph
' ԭʼ�仯
    Selection.TypeText Text:="(1) ԭʼ�仯����"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.TypeText Text:="�������ɼ������ݣ�" + prod + "��" + ctrl + "��ԭʼ�仯������ͼ" + Str(picIdx) + ".1��ʾ��Ϊ����Աȣ�����ָ���������ֵ�����˱�׼������"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    If (prod <> "��̿����" And prod <> "[��ˮ�¶�]") Then
        Selection.TypeText Text:="���⣬Ϊ�˸��õ�����ʱ�ʹ����Ч��������ѡȡ��ĳ��������ı仯���ƽ��бȽϡ�"
        Selection.Style = ActiveDocument.Styles("������ʽ")
    End If
    Selection.TypeParagraph
    
    
    Selection.InlineShapes.AddPicture FileName:= _
        FilePath + "\�ͺ�\" + prod + "��" + ctrl + "�Ĳ���ͼ(δ�ͺ���).png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '����
    Selection.TypeParagraph
    
    Selection.TypeText Text:="ͼ" + Str(picIdx) + ".1. " + prod + "��" + ctrl + "���ԭʼ�仯����"
    Selection.Style = ActiveDocument.Styles("ͼע��ʽ")
    Selection.TypeParagraph
    
' ����Է�������
    
    Selection.TypeText Text:="(2) ����Է�������"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.TypeText Text:="��������������ԭʼ�仯���ߣ���������Է��������������ͼ" + Str(picIdx) + _
                            ".2��ʾ�����ʱ���ͺ�Χ�����趨������ȷ��" + prod + "�����" + ctrl + "���ͺ�ʱ��Ϊ" + Str(time(j * 9 + i)) + "���ӡ�"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.InlineShapes.AddPicture FileName:= _
         FilePath + "\�ͺ�\" + prod + "��" + ctrl + "���ͺ�ʱ�����ͼ.png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '����
    Selection.TypeParagraph
    
    
    Selection.TypeText Text:="ͼ" + Str(picIdx) + ".2. " + prod + "��" + ctrl + "������Է����������"
    Selection.Style = ActiveDocument.Styles("ͼע��ʽ")
    Selection.TypeParagraph
    
' (3) �����ͺ�ʱ����д���������
    
    Selection.TypeText Text:="(3) �����ͺ�ʱ����д���������"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.TypeText Text:="��������õ�����������ʱ�ͷ��������������ԭʼ���߽��е�������������ָ�����" + prod + "��ǰ����" + Str(time(j * 9 + i)) + _
                            "���ӣ����Ի�����������Ķ�Ӧ���ߡ�"
    
    '����ͼ" + Str(picIdx) + ".3��ʾ���ӽ���п��Կ���������ʱ�ʹ������������֮����нϺõĶ�Ӧ��ϵ��"
    
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.InlineShapes.AddPicture FileName:= _
        FilePath + "\�ͺ�\" + prod + "��" + ctrl + "�Ĳ���ͼ(�ͺ����).png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '����
    Selection.TypeParagraph
    
    
    Selection.TypeText Text:="ͼ" + Str(picIdx) + ".3. " + prod + "��" + ctrl + "���ͺ�������"
    Selection.Style = ActiveDocument.Styles("ͼע��ʽ")
    Selection.TypeParagraph
    
    Next i
    Next j

End Sub
Sub ����ͼ��С()
'
' ��3 ��
'
'
    Dim n 'ͼƬ����

    ' On Error Resume Next '���Դ���
    
    For n = 1 To ActiveDocument.InlineShapes.Count 'InlineShapes ���� ͼƬ
    
    ActiveDocument.InlineShapes(n).Height = 8 * 28.35 '����ͼƬ�߶�Ϊ 6cm��1cm����28.35px��
    
    ActiveDocument.InlineShapes(n).Width = 10.67 * 28.35 '����ͼƬ��� 6cm
    
    Next n
    
End Sub

Sub ��ӡ·��()
    Dim FilePath As String
    
    FilePath = Application.Path
    Selection.TypeText Text:=FilePath
End Sub

Sub main2()
    Dim MyCtrl()
    MyCtrl = Array("�ȷ��¶�", "�ͷ����", "������", "�紵����", "���ſ����", "��̿����")
    
    Dim MyProd()
    MyProd = Array("�ȷ�ѹ��", "͸����ָ��", "�ķ綯��", "����ȼ���¶�", "ú��������", "¯���¶ȼ���", "¯���¶ȼ���", "¯��ú��������", "��ˮ�¶�", "[Ti]", "[Si]")
    
    FilePath = "C:\Users\Administrator\Desktop\��ʱ�ͱ���\figs\" '��ȡ����·��,�����ȡpngͼƬ
    
    Dim i As Long
    Dim j As Long
    
    
    For j = 0 To 10
    For i = 0 To 5
    
    'i = 0
    'j = 0
    
    picIdx = j * 6 + i + 1 'ͼƬ�����
    ctrl = MyCtrl(i)       '���Ʋ�����
    prod = MyProd(j)       '����������
    
    
    
'����
    
    Selection.TypeText Text:=Str(picIdx) + ". " + prod + "��" + ctrl
    Selection.Style = ActiveDocument.Styles("С������ʽ")
    Selection.TypeParagraph
    
' ԭʼ�仯

    Selection.TypeText Text:="(1) ԭʼ�仯����"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.TypeText Text:="�������ɼ������ݣ�" + prod + "��" + ctrl + "��ԭʼ�仯������ͼ" + Str(picIdx) + ".1��ʾ��Ϊ����Աȣ�����ָ���������ֵ�����˱�׼������"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    If (prod <> "��̿����" And prod <> "��ˮ�¶�" And ctrl <> "���ſ����") Then
        Selection.TypeText Text:="���⣬Ϊ�˸��õ�����ʱ�ʹ����Ч��������ѡȡ��ĳ��������ı仯���ƽ��бȽϡ�"
        Selection.Style = ActiveDocument.Styles("������ʽ")
    End If
    Selection.TypeParagraph
    
    Selection.InlineShapes.AddPicture FileName:=FilePath + prod + "��" + ctrl + "�Ĳ���ͼ(δ�ͺ���).png", LinkToFile:=False, SaveWithDocument:=True
    Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '����
    Selection.TypeParagraph
    
    Selection.TypeText Text:="ͼ" + Str(picIdx) + ".1. " + prod + "��" + ctrl + "���ԭʼ�仯����"
    Selection.Style = ActiveDocument.Styles("ͼע��ʽ")
    Selection.TypeParagraph
    
    
'����Է�������
    
    Selection.TypeText Text:="(2) ����Է�������"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
'    Selection.TypeText Text:="��������������ԭʼ�仯���ߣ���������Է��������������ͼ" + Str(picIdx) + _
'                           ".2��ʾ�����ʱ���ͺ�Χ�����趨������ȷ��" + prod + "�����" + ctrl + "���ͺ�ʱ��Ϊ" + Str(time(j * 9 + i)) + "���ӡ�"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.InlineShapes.AddPicture FileName:= _
         FilePath + prod + "��" + ctrl + "���ͺ�ʱ�����ͼ.png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '����
    Selection.TypeParagraph
    
    
    Selection.TypeText Text:="ͼ" + Str(picIdx) + ".2. " + prod + "��" + ctrl + "������Է����������"
    Selection.Style = ActiveDocument.Styles("ͼע��ʽ")
    Selection.TypeParagraph
    
'(3)�����ͺ�ʱ����д���������
    
    Selection.TypeText Text:="(3) �����ͺ�ʱ����д���������"
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
   ' Selection.TypeText Text:="��������õ�����������ʱ�ͷ��������������ԭʼ���߽��е�������������ָ�����" + prod + "��ǰ����" + Str(time(j * 9 + i)) + _
    '                        "���ӣ����Ի�����������Ķ�Ӧ���ߡ�"
    
    '����ͼ" + Str(picIdx) + ".3��ʾ���ӽ���п��Կ���������ʱ�ʹ������������֮����нϺõĶ�Ӧ��ϵ��"
    
    Selection.Style = ActiveDocument.Styles("������ʽ")
    Selection.TypeParagraph
    
    Selection.InlineShapes.AddPicture FileName:= _
        FilePath + prod + "��" + ctrl + "�Ĳ���ͼ(�ͺ����).png", _
         LinkToFile:=False, SaveWithDocument:=True
        Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter '����
    Selection.TypeParagraph
    
    
    Selection.TypeText Text:="ͼ" + Str(picIdx) + ".3. " + prod + "��" + ctrl + "���ͺ�������"
    Selection.Style = ActiveDocument.Styles("ͼע��ʽ")
    Selection.TypeParagraph
    
    Next i
    Next j

End Sub

