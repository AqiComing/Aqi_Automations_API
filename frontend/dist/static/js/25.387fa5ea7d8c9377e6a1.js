webpackJsonp([25],{20:function(t,e,a){"use strict";function o(t){a(516)}Object.defineProperty(e,"__esModule",{value:!0});var n=a(394),r=a.n(n);for(var i in n)"default"!==i&&function(t){a.d(e,t,function(){return n[t]})}(i);var s=a(518),d=a(1),l=o,c=d(r.a,s.a,!1,l,"data-v-b33ddbca",null);e.default=c.exports},360:function(t,e,a){t.exports=a.p+"static/img/userphoto.6d73d26.jpg"},394:function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0}),e.default={data:function(){return{tabPosition:"top",project_id:"",sysName:"自动化测试平台",collapsed:!1,sysUserName:"",sysUserAvatar:""}},methods:{handleselect:function(t,e){},onSubmit:function(){console.log("submit!")},logout:function(){var t=this;this.$confirm("确认退出吗?","提示",{}).then(function(){sessionStorage.removeItem("token"),t.$router.push("/login")}).catch(function(){})},showMenu:function(t,e){this.$refs.menuCollapsed.getElementsByClassName("submenu-hook-"+t)[0].style.display=e?"block":"none"}},mounted:function(){var t=sessionStorage.getItem("username");t&&(name=JSON.parse(t),this.sysUserName=name||""),this.project_id=this.$route.params.project_id}}},516:function(t,e,a){var o=a(517);"string"==typeof o&&(o=[[t.i,o,""]]),o.locals&&(t.exports=o.locals);a(14)("1a275e51",o,!0,{})},517:function(t,e,a){e=t.exports=a(13)(!1),e.push([t.i,".container[data-v-b33ddbca]{position:absolute;top:0;bottom:0;width:100%}.container .header[data-v-b33ddbca]{height:60px;line-height:60px;background:#20a0ff;color:#eeefff}.container .header .userinfo[data-v-b33ddbca]{text-align:right;padding-right:35px;float:right}.container .header .userinfo .userinfo-inner[data-v-b33ddbca]{cursor:pointer;color:#fff}.container .header .userinfo .userinfo-inner img[data-v-b33ddbca]{width:40px;height:40px;border-radius:20px;margin:10px 0 10px 10px;float:right}.container .header .logo[data-v-b33ddbca]{height:60px;font-size:22px;padding-left:20px;padding-right:20px;border-color:hsla(62,77%,76%,.3);border-right-width:1px;border-right-style:solid}.container .header .logo img[data-v-b33ddbca]{width:40px;float:left;margin:10px 10px 10px 18px}.container .header .logo .txt[data-v-b33ddbca]{color:#fff}.container .header .logo-width[data-v-b33ddbca]{width:230px}.container .header .logo-collapse-width[data-v-b33ddbca]{width:60px}.container .header .tools[data-v-b33ddbca]{padding:0 23px;width:14px;height:60px;line-height:60px;cursor:pointer}.container .title[data-v-b33ddbca]{width:200px;float:left;color:#475669;font-size:25px;margin:15px;margin-left:35px;margin-bottom:0;font-family:PingFang SC}",""])},518:function(t,e,a){"use strict";var o=function(){var t=this,e=t.$createElement,o=t._self._c||e;return o("el-row",{staticClass:"container"},[o("el-col",{staticClass:"header",attrs:{span:24}},[o("el-col",{staticClass:"logo",class:t.collapsed?"logo-collapse-width":"logo-width",attrs:{span:10}},[o("router-link",{staticStyle:{"text-decoration":"none",color:"#FFFFFF"},attrs:{to:"/projectList"}},[t._v(t._s(t.collapsed?"":t.sysName))])],1),t._v(" "),o("el-col",{staticClass:"userinfo",attrs:{span:4}},[o("el-dropdown",{attrs:{trigger:"hover"}},[o("span",{staticClass:"el-dropdown-link userinfo-inner"},[o("img",{attrs:{src:a(360)}}),t._v(" "+t._s(t.sysUserName))]),t._v(" "),o("el-dropdown-menu",{attrs:{slot:"dropdown"},slot:"dropdown"},[o("el-dropdown-item",{attrs:{divided:""},nativeOn:{click:function(e){return t.logout(e)}}},[t._v("退出登录")])],1)],1)],1)],1),t._v(" "),o("el-col",{attrs:{span:24}},[[o("el-menu",{directives:[{name:"show",rawName:"v-show",value:!t.collapsed,expression:"!collapsed"}],staticClass:"el-menu-vertical-demo",attrs:{"default-active":t.$route.path,mode:"horizontal","unique-opened":""},on:{select:t.handleselect}},[t._l(t.$router.options.routes,function(e){return e.projectHidden?t._e():[t._l(e.children,function(e,a){return[e.leaf?o("el-menu-item",{key:e.path,attrs:{index:e.path}},[e.child?t._e():[o("router-link",{staticStyle:{"text-decoration":"none",color:"#000000"},attrs:{to:{name:e.name,params:{id:t.project_id}}}},[o("div",[t._v("\n\t\t\t\t\t\t\t\t\t\t"+t._s(e.name)+"\n\t\t\t\t\t\t\t\t\t")])])],t._v(" "),e.child?[o("router-link",{staticStyle:{"text-decoration":"none",color:"#000000"},attrs:{to:{name:e.children[0].name,params:{id:t.project_id}}}},[o("div",[t._v("\n\t\t\t\t\t\t\t\t\t\t"+t._s(e.name)+"\n\t\t\t\t\t\t\t\t\t")])])]:t._e()],2):t._e(),t._v(" "),e.leaf?t._e():o("el-submenu",{attrs:{index:a+""}},[o("template",{slot:"title"},[t._v(t._s(e.name))]),t._v(" "),t._l(e.children,function(e){return o("el-menu-item",{key:e.path,attrs:{index:e.path}},[t._v("\n\t\t\t\t\t\t\t\t"+t._s(e.name)+"\n\t\t\t\t\t\t\t")])})],2)]})]})],2)],t._v(" "),o("strong",{staticClass:"title"},[t._v(t._s(t.$route.name))])],2),t._v(" "),o("el-col",{attrs:{span:24}},[o("transition",{attrs:{name:"fade",mode:"out-in"}},[o("router-view")],1)],1)],1)},n=[],r={render:o,staticRenderFns:n};e.a=r}});