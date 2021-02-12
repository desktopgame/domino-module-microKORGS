import xml.etree.ElementTree as ET
import copy
from xml.dom import minidom
from typing import List, Dict, Text

def str_strip(s: str):
    if s:
        return s.strip()
    return s

def copy_tree(dst: ET.Element, src: ET.Element):
    for child in src:
        childDst: ET.Element = ET.SubElement(dst, child.tag, child.attrib)
        childDst.text = str_strip(child.text)
        copy_tree(childDst, child)

# 基本的な設定を流用するため、デフォルト設定をパース
defaultSetting = ET.parse("default.xml")
defaultSettingRoot = defaultSetting.getroot()

# ルートを作成する
root = ET.Element("ModuleData", {
    "Name": "microKORGS",
    "Folder": "",
    "Priority": "1",
    "FileCreator": "desktopgame",
    "FileVersion": "1.00",
    "WebSite": "https://github.com/desktopgame"
})
instruments = ET.SubElement(root, "InstrumentList")

# バンクと番号を対応づけるように要素生成
banks: int = 8
bankTable: List[str] = ["A", "B", "C", "D"]
offsetTable: List[int] = [11, 21, 31, 41, 51, 61, 71, 81]
categoryTable: List[str] = ["TRANCE", "TECHNO/HOUSE", "ELECTRONICA", "D'n'B/BREAKS", "HIPHOP", "RETRO", "S.E./HIT", "VOCODER"]
mapDict: Dict[str, ET.Element] = {}
for level in range(0, 256):
    bankNo: int = int(level / 64)
    # A, B, C, Dに対応する要素を作成
    if bankTable[bankNo] not in mapDict:
        mapDict[bankTable[bankNo]] = ET.SubElement(instruments, "Map", {
            "Name": bankTable[bankNo]
        })
    category: ET.Element = mapDict[bankTable[bankNo]]
    bankOffset: int = int(int(level % 64) / 8)
    programNo: int = offsetTable[bankOffset] + (int(level % 8))
    # カテゴリ名取得
    categoryName = ""
    for i in range(0, 8):
        start: int = offsetTable[i]
        end: int = start + 7
        if programNo >= start and programNo <= end:
            categoryName = categoryTable[i]
            break
    # インストゥルメントの名前を生成
    name: str = f"{categoryName}_{bankTable[bankNo]}{programNo}_{level}"
    print(name)
    # インストゥルメントに対応する要素を作成
    pc = level
    if pc >= 128:
        pc = level % 128
    inst: ET.Element = ET.SubElement(category, "PC", {
        "Name": name,
        "PC": f"{pc+1}"
    })
    if bankNo <= 1:
        instBank: ET.Element = ET.SubElement(inst, "Bank", {
            "Name": name,
        })
    else:
        # これでC,Dのバンクのための設定
        instBank: ET.Element = ET.SubElement(inst, "Bank", {
            "Name": name,
            "LSB": f"{0}",
            "MSB": f"{1}"
        })
# 基本となる設定の作成
copySettings: List[str] = ["ControlChangeMacroList", "TemplateList", "DefaultData"]
child: ET.Element
for child in defaultSettingRoot:
    if child.tag not in copySettings:
        continue
    dst: ET.Element = ET.SubElement(root, child.tag, child.attrib)
    dst.text = str_strip(child.text)
    copy_tree(dst, child)
    #clone = copy.deepcopy(child)
    #root.append(clone)

#tree = ET.ElementTree(root)
#tree.write('microKORGS.xml', encoding="Shift_JIS", xml_declaration=True)
xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
with open("microKORGS.xml", "w") as f:
    f.write(xmlstr)