from django.conf.urls import url

from api_test.views import user, project, dynamic, global_host, member, api_group, api, test_case_group

urlpatterns=[
    url(r'user/login',user.ObtainAuthToken.as_view()),
    url(r"project/project_list",project.ProjectList.as_view()),
    url(r'project/add_project',project.AddProject.as_view()),
    url(r'project/update_project',project.UpdateProject.as_view()),
    url(r'project/del_project',project.DelProject.as_view()),
    url(r'project/enable_project',project.EnableProject.as_view()),
    url(r'project/disable_project',project.EnableProject.as_view()),
    url(r'title/project_info',project.ProjectInfo.as_view()),
    url(r'dynamic/dynamic', dynamic.Dynamic.as_view()),
    url(r'global/add_host', global_host.AddHost.as_view()),
    url(r'global/host_total', global_host.HostTotal.as_view()),
    url(r'global/del_host', global_host.DelHost.as_view()),
    url(r'global/update_host', global_host.UpdateHost.as_view()),
    url(r'global/disable_host', global_host.EnableHost.as_view()),
    url(r'global/enable_host', global_host.EnableHost.as_view()),
    url(r'member/project_member', member.ProjectMemberList.as_view()),
    url(r'member/email_config', member.EmailConfig.as_view()),
    url(r'member/get_email', member.GetEmail.as_view()),
    url(r'api/group', api_group.APIGroupView.as_view()),
    url(r'api/add_group', api_group.APIGroupAdd.as_view()),
    url(r'api/del_group', api_group.DelAPIGroup.as_view()),
    url(r'api/update_name_group', api_group.UpdateAPIGroup.as_view()),
    url(r'api/add_api', api.AddAPI.as_view()),
    url(r'api/api_list', api.APIList.as_view()),
    url(r'api/api_info', api.APIInfoView.as_view()),
    url(r'api/update_api', api.UpdateAPI.as_view()),
    url(r'api/del_api', api.DelAPI.as_view()),
    url(r'automation/add_group', test_case_group.AddGroup.as_view()),
    url(r'automation/group', test_case_group.Group.as_view()),
    url(r'automation/del_group', test_case_group.DelGroup.as_view()),
    url(r'automation/update_name_group', test_case_group.UpdateGroup.as_view()),

]
