from django.conf.urls import url

from api_test.views import user, project, dynamic, global_host

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
    url(r'global/disable_host', global_host.UpdateHost.as_view()),
    url(r'global/update_host', global_host.UpdateHost.as_view()),
]
