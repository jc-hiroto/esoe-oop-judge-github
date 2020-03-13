import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.db.models import Max
from django.contrib.auth.models import User
from .models import Problem, Submission

from django.contrib.auth import views as auth_views

from django.contrib.auth.forms import PasswordChangeForm
from .forms import ProfileUpdateGithubForm


@login_required
def index(request):
    # you may change this to use a different problem as sample problem
    sample_problem = Problem.objects.get(pk=1)

    return render(request,
                  'judge/index.html',
                  {'github_account': config.GITHUB_ACCOUNT,
                   'sample_problem': sample_problem})


def login(request):
    # users should not be able to log in again if they're already logged in
    if request.user.is_authenticated():
        messages.error(request,
                       'You are already logged in.')
        return HttpResponseRedirect(reverse('judge:index'))
    else:
        return auth_views.login(request, template_name='judge/login.html')


def logout(request):
    # users should not be able to log out if they're not logged in yet
    if not request.user.is_authenticated():
        messages.error(request,
                       'You are not logged in yet.')
        return HttpResponseRedirect(reverse('judge:index'))
    else:
        return auth_views.logout(request, next_page='judge:index')


@login_required
def problem_list(request):
    user = request.user
    profile = user.profile

    problem_info_list = []
    for problem in Problem.objects.all():
        if problem.staff_viewable_only and not user.is_staff:
            continue

        profile_solved = profile.solved_problems.filter(pk=problem.pk).exists()
        problem_info_list.append({
            'problem': problem,
            'profile_solved': profile_solved
        })

    return render(request,
                  'judge/problem_list.html',
                  {'problem_info_list': problem_info_list})


@login_required
def problem_detail(request, pk):
    user = request.user
    profile = user.profile

    problem = get_object_or_404(Problem, pk=pk)
    if problem.staff_viewable_only and not user.is_staff:
        messages.error(request,
                       'Permission denied.')
        return HttpResponseRedirect(reverse('judge:index'))

    profile_submission_list = problem.submission_set.filter(profile=profile)
    profile_solved = profile.solved_problems.filter(pk=problem.pk).exists()

    submitted_file_info_list = []
    for f in problem.requiredfile_set.filter(via='S'):
        submitted_file_info_list.append({
            'filename': f.filename
        })
    provided_file_info_list = []
    for f in problem.requiredfile_set.filter(via='P'):
        provided_file_info_list.append({
            'filename': f.filename,
            'static_path': os.path.join(
                os.path.basename(config.JUDGE_STATIC_PROBLEMS_DIR),
                str(problem.pk),
                f.filename
            )
        })

    # handle submission
    if request.method == 'POST':
        now = timezone.now()

        # no submissions are allowed after deadline
        if now > problem.deadline_datetime:
            messages.error(request, 'Sorry, it is already over the deadline.')
        else:
            submission = Submission(problem=problem,
                                    profile=profile,
                                    submission_datetime=now)
            submission.save()

            # judge (without waiting)
            subprocess.Popen([os.path.join(config.VIRTUALENV_BIN_DIR, 'python'),
                              os.path.join(config.JUDGE_BIN_DIR, 'judge.py'),
                              str(submission.pk)])

            messages.success(request, 'Submitting. Refresh to see the results.')
        return HttpResponseRedirect(reverse('judge:problem_detail', kwargs={'pk': pk}))

    return render(request,
                  'judge/problem_detail.html',
                  {'problem': problem,
                   'profile_submission_list': profile_submission_list,
                   'profile_solved': profile_solved,
                   'submitted_file_info_list': submitted_file_info_list,
                   'provided_file_info_list': provided_file_info_list})


@login_required
def profile(request):
    user = request.user
    profile = user.profile

    # unbound forms to be used later
    unbound_update_github_form = ProfileUpdateGithubForm(instance=profile,
                                                         initial={'github_account':
                                                                  profile.github_account,
                                                                  'github_repository':
                                                                  profile.github_repository})
    unbound_password_change_form = PasswordChangeForm(user=user)

    # handle forms
    if request.method == 'POST':
        update_github_form = ProfileUpdateGithubForm(data=request.POST,
                                                     instance=profile,
                                                     initial={'github_account':
                                                              profile.github_account,
                                                              'github_repository':
                                                              profile.github_repository})
        password_change_form = PasswordChangeForm(data=request.POST, user=user)

        # for it to be regarded as successful (such that the user gets
        # redirected back to profile), all changed forms must be valid and saved
        # already; otherwise, render the view with all forms again (with
        # unchanged ones replaced by unbound ones, so as to clean their errors),
        # in order for the user to know what errors have occurred
        n_undone_forms = update_github_form.has_changed() + password_change_form.has_changed()

        if update_github_form.has_changed():
            if update_github_form.is_valid():
                update_github_form.save()
                n_undone_forms -= 1

                messages.success(request,
                                 'GitHub settings successfully updated.')
        else:
            update_github_form = unbound_update_github_form

        if password_change_form.has_changed():
            if password_change_form.is_valid():
                password_change_form.save()
                n_undone_forms -= 1

                messages.success(request,
                                 'Password successfully changed. Please log in again.')
        else:
            password_change_form = unbound_password_change_form

        if n_undone_forms == 0:
            return HttpResponseRedirect(reverse('judge:profile'))
    else:
        update_github_form = unbound_update_github_form
        password_change_form = unbound_password_change_form

    return render(request,
                  'judge/profile.html',
                  {'profile': profile,
                   'update_github_form': update_github_form,
                   'password_change_form': password_change_form})


@login_required
def submission_detail(request, pk):
    user = request.user
    profile = user.profile

    submission = get_object_or_404(Submission, pk=pk)

    # if the profile isn't the owner of this submission, and it isn't a staff
    # either, then it shouldn't see this submission
    if submission.profile != profile and not user.is_staff:
        messages.error(request,
                       'Permission denied.')
        return HttpResponseRedirect(reverse('judge:index'))

    # display submitted files (only when status != 'SU' and status != 'SE')
    submitted_file_info_list = []
    if submission.status != 'SU' and submission.status != 'SE':
        submitted_filenames = [f.filename for f in submission.problem.requiredfile_set.filter(via='S')]
        for filename in submitted_filenames:
            # here, we specifically open the file in binary mode, read it, and
            # then decode it with UTF-8, such that reading submitted files in
            # other encodings (for example, those uploaded from Windows) won't
            # cause a problem
            with open(os.path.join(config.JUDGE_SUBMISSIONS_DIR, str(submission.pk), filename), 'rb') as f:
                submitted_file_info_list.append({
                    'filename': filename,
                    'content': f.read().decode('utf-8', 'replace')
                })

    return render(request,
                  'judge/submission_detail.html',
                  {'submission': submission,
                   'submitted_file_info_list': submitted_file_info_list})
