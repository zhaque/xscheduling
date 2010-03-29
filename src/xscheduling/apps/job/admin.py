from django.contrib import admin
from job.models import Job, Milestone, Task, JobState, Note

admin.site.register(Job)
admin.site.register(Milestone)
admin.site.register(Task)
admin.site.register(JobState)
admin.site.register(Note)


