import re
import logging

from django.shortcuts import render , get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core import management
from .models import Athlete
from .models import Stalker
from .forms import AddAthleteForm





def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def stalkerGetOrCreate(usr):
    """
    If a user does not have a stalker object (list of athletes they are following),
    create it.

    Returns Stalker object
    """
    try:
        user = Stalker.objects.get(user=usr)
    except Stalker.DoesNotExist:
        user = Stalker(user=usr)
        user.save()
        return user

    return user


@csrf_protect
def add_athlete(request):

    if not request.user.is_authenticated():
        return redirect('/accounts/login/')
    else:

        if request.method == 'GET':
            form = AddAthleteForm()
            
        elif request.method == 'POST':
            form = AddAthleteForm(request.POST)

            if form.is_valid():
                
                
                already_created = Athlete.objects.filter(created_by = request.user)

                if (len(already_created) >= settings.MAX_CREATED_ALLOWED):
                    form.add_error(form.errors, "You have already created the max number of custom athletes. Contact admin for help.")
                    return render(request, 'athlete_add.html' , {'form' : form})


                name  = form.cleaned_data['name']
                school  = form.cleaned_data['school']

                names = name.split()
                if (len(names) != 2):
                    form.add_error(form.errors, "Name entered is in incorrect format")
                    return render(request, 'athlete_add.html' , {'form' : form})

                
                search_term = names[0] + " " + names[1] + " " + school 
                entry_query = get_query(search_term, ['name', 'school',])
                search_results = Athlete.objects.filter(entry_query)[0:1]
                
                results = search_results

                if (len(results) != 0):
                    
                    possible_meant = ""
                    for x in results:
                        possible_meant += x.name + "(" + x.school + ")\n"
                   
                    form.add_error(form.errors, "Athlete(s) " + possible_meant + " already seem to exist.")
                    return render(request, 'athlete_add.html' , {'form' : form})

                new_athlete = Athlete(name = name, school = school, url = (name.replace(" ","_") + "/" +school ) , created_by = request.user )

                new_athlete.save()

                user = stalkerGetOrCreate(request.user)
                user.following_athletes.add(new_athlete)

                
                return render(request, 'athlete_add.html' , {'form' : form , 'success_added' : new_athlete})
                

                


        return render(request, 'athlete_add.html' , {'form' : form})
    

def meetPing(request):
	if request.user.is_superuser:
		management.call_command('runcrons')
		return HttpResponse('MeetPing Success!')
	else:
		return HttpResponseForbidden()
@csrf_protect
def home(request):
    """
    Handles all GET and POST requests on the homepage
    """

    log = logging.getLogger(settings.LOG_OBJECT)
    
    log.info(request.META['HTTP_HOST'] + " requested homepage")
    
    athletes = None
    results = None
    if request.user.is_authenticated():
        user = stalkerGetOrCreate(request.user)
        athletes = user.following_athletes.all()

    if request.method == "POST":
       
        wants_to_follow = request.POST.getlist('following_athletes')
        

        if request.user.is_authenticated():
            
            user = stalkerGetOrCreate(request.user)
            
            print settings.MAX_FOLLOWING_ALLOWED

            if (len(wants_to_follow)) > settings.MAX_FOLLOWING_ALLOWED:
                log.warning(request.user.get_username() + " tried to follow too many users")
                return render(request, 'home.html',  { 'validation_error': settings.MAX_FOLLOWING_ALLOWED , 'following': athletes, 'userinfo': "userinfo"}  )
           
            try:
                if ([ int(x) for x in wants_to_follow ] == list(user.following_athletes.all().values_list('pk', flat=True))):
                    log.info(request.user.get_username() + " clicked save without making changes")
                    return render(request, 'home.html',  { 'following': athletes, 'success_change' : "success", 'userinfo': "user-info"}  )
            except ValueError:
                log.error(request.user.get_username() + " fabricated a POST request. Ban?")
                return HttpResponseForbidden()

            user.following_athletes.clear()

            for athlete_id in wants_to_follow:
                athlete = get_object_or_404(Athlete, pk=athlete_id)
                user.following_athletes.add(athlete)

        log.info(request.user.get_username() + " has changed who they are following")
        return render(request, 'home.html',  { 'following': athletes, 'success_change' : "success", 'userinfo': "user-info"}  )
       
    
    elif ('q' in request.GET) and request.GET['q'].strip():
        search_term = request.GET['q']

        if (search_term == "" or not request.user.is_authenticated()):
            return render(request, 'home.html')

        entry_query = get_query(search_term, ['name', 'school',])
        search_results = Athlete.objects.filter(entry_query)[0:settings.MAX_QUERY_RESULTS]
        results = search_results
        log.info(request.user.get_username() + " searched for: \"" + str(search_term) + "\"")
        return render(request, 'home.html',  {'results': results , 'following': athletes , 'valid_query': search_term, 'userinfo': "user-info"}  )
    
    return render(request, 'home.html',  { 'following': athletes}  )

#should put all in dict, set those unneded to None and check for none in home template
