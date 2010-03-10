from django.contrib import admin
from job.models import Job, Milestone, Task, JobType, JobState

admin.site.register(Job)
admin.site.register(Milestone)
admin.site.register(Task)
admin.site.register(JobType)
admin.site.register(JobState)


