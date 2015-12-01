from django.shortcuts import render

from .models import Card, Scan
from .models import CardForm

from django.template import RequestContext, loader

from django.db import connection, transaction

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Create your views here.

class CardDelete(DeleteView):
    model = Card
    success_url = reverse_lazy('ms:cards')
    
    #def deleteq(self, request, *args, **kwargs):
    #    response = super(CardDelete, self).delete(request, *args, **kwargs)
    #    card = self.get_object()
     #   print card.id
    #    Scan.objects.filter(fk_card_id=card.id).update(fk_card_id=0)
     #   card.delete()
    #    return response
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        Scan.objects.filter(fk_card_id=self.object.id).update(fk_card_id=0)
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())
    #card = DeleteView.get_object(self)
    #print card.id
    #Scan.objects.filter(fk_card_id=card.id).update(fk_card_id=0)
    
    
    
 

def cards(request, sort='-count'):
    # Data retrieval operation - no commit required
           
    #cursor = connection.cursor()
    #cursor.execute('SELECT * FROM ms_card WHERE 1')# [self.baz])
    #row = cursor.fetchone()
    #print row
    #cards = cursor.fetchall()
    #print cards
    
    
    #for field in Card._meta.fields:
    #    print field.get_attname_column()
    
    if sort=='all':
        cards = Card.objects.order_by('pk')  
    else:
        cards = Card.objects.filter(count__gt=0).order_by(sort)
    #cards = Card.objects.order_by('-count')
    
    
    
    #for card in cards:
    #    card.count = Scan.objects.filter(fk_card=card).count()



    
    
    context = RequestContext(request, {
            'cards': cards })
    return render(request, 'ms/cards.html', context)

def scan_delete(request, pk):
    scan = Scan.objects.get(pk=pk)
    
    c = Card.objects.get(pk=scan.fk_card_id)
    c.count = c.count - 1 
    c.save()
    
    scan.fk_card_id = 0
    scan.save()
    
    return card(request, c.pk)

def card(request, pk):
    if pk=='0':
        scans = Scan.objects.filter(fk_card_id=0).order_by('position')
        #scans = Scan.objects.order_by('order')
        context = RequestContext(request, {
            'scans': scans })
        return render(request, 'ms/card.html', context) 
    
    card = Card.objects.get(pk=pk)
    form = CardForm(instance = card)
    
    if request.method == 'POST':
        print request.POST
        if 'save' in request.POST:
            form = CardForm(request.POST, instance=card)
            card.name = form.data['name']
            card.price = form.data['price']
            card.save()
            return HttpResponseRedirect('/ms/card/'+str(pk))
            #if form.is_valid():
            #    form.save() 
            #    return HttpResponseRedirect('/ms/card/'+str(pk))
              
    
    scans = Scan.objects.filter(fk_card=card).order_by('order')
     
    
    context = RequestContext(request, {
            'form': form,
            'card': card,
            'scans': scans })
    return render(request, 'ms/card.html', context)  