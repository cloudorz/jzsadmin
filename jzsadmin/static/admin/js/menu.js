
a = new dTree('a');
a.config.folderLinks=false;
a.config.useStatusText=true;
a.config.useCookies=false;
a.config.closeSameLevel=false;

a.add(0,-1,'<B>家政发布管理</B>','javascript: void(0);');

a.add(1, 0,'发布管理','');
a.add(2, 1,'审核列表','/admin/entry/status/');

a.add(10, 0,'内容管理','');
a.add(11, 10,'信息条目','/admin/entry/');
a.add(12, 10,'列表分类','/admin/cate/');
a.add(13, 10,'城市列表','/admin/city/');

document.write(a);
eval("a.closeAll();");
