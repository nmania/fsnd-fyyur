#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key = True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key = True)
    start_time = db.Column(db.DateTime, nullable = False)
    artist = db.relationship('Artist', backref = db.backref('shows', cascade = "all, delete-orphan"))
    venue = db.relationship('Venue', backref = db.backref('shows', cascade = "all, delete-orphan"))



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(120), nullable = False)
    facebook_link = db.Column(db.String(120), nullable = False)
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default = True)

    artists = association_proxy('shows', 'artist' , cascade_scalar_deletes= True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable = False)
    seeking_description = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, default = True)
    website = db.Column(db.String(120))

    venues = association_proxy('shows', 'venue' , cascade_scalar_deletes= True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    city_state = set([])
    venues = Venue.query.all()
    for v in venues:
        city_state.add((v.city, v.state))
    for cs in city_state:
        ven = []
        d = {"city": cs[0], "state": cs[1], "venues": []}
        for v in venues:
            num = 0
            for show in v.shows:
                if show.start_time > datetime.now():
                    num += 1
            if v.city == cs[0] and v.state == cs[1]:
                ven.append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows" : num
                })
        d["venues"] = ven
        data.append(d)


    # data=[{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #        }]
    #      }, {
    #         "city": "New York",
    #         "state": "NY",
    #         "venues": [{
    #             "id": 2,
    #             "name": "The Dueling Pianos Bar",
    #             "num_upcoming_shows": 0,
    #         }]
    #      }
    # ]
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_keyword = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_keyword))).all()
    response = {"count": len(venues)}
    data = []
    for v in venues:
        num = 0
        for show in v.shows:
            if show.start_time > datetime.now():
                num += 1
        data.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": num
            })
    response["data"] = data



    # response={
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id


    venue = Venue.query.filter(Venue.id == venue_id).first();
    past_shows_list = []
    up_shows_list = []

    for show in venue.shows:
        if show.start_time > datetime.now():
            up_shows_list.append({
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })
        else:
            past_shows_list.append({
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })

    data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(', '),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": up_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(up_shows_list)
    }


    # data1={
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #       "artist_id": 4,
    #       "artist_name": "Guns N Petals",
    #       "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #       "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2={
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3={
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #       "artist_id": 5,
    #       "artist_name": "Matt Quevedo",
    #       "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #       "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #       "artist_id": 6,
    #       "artist_name": "The Wild Sax Band",
    #       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #       "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #       "artist_id": 6,
    #       "artist_name": "The Wild Sax Band",
    #       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #       "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #       "artist_id": 6,
    #       "artist_name": "The Wild Sax Band",
    #       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #       "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    create_error = False
    query_error = False
    data = {}
    id = None
    try:
        venue = Venue(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        address = request.form['address'],
        phone = request.form['phone'],
        facebook_link = request.form['facebook_link'],
        genres = ", ".join(request.form.getlist('genres')),
        image_link = request.form['image_link'] if 'image_link' in request.form else None,
        website = request.form['website'] if 'website' in request.form else None,
        seeking_talent = True if request.form['seeking_talent'] == "Yes" else False,
        seeking_description = request.form['seeking_description'] if 'seeking_description' in request.form else None
        )
        db.session.add(venue)
        db.session.commit()
        id = venue.id
    except:
        create_error = True
        print(sys.exc_info(), request.form.getlist('genres'))
        db.session.rollback()
    finally:
        db.session.close()

    try:
        data = Venue.query.filter_by(id = id).first()
    except:
        query_error = True
        print(sys.exc_info())

    # on successful db insert, flash success
    if create_error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        if query_error:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        else:
            flash('Venue ' + data.name + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        ven = Venue.query.filter(Venue.id == venue_id).first()
        db.session.delete(ven)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
        "id": artist.id,
        "name": artist.name
        })

    # data=[{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_keyword = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_keyword))).all()
    response = {"count": len(artists)}
    data = []
    for a in artists:
        num = 0
        for show in a.shows:
            if show.start_time > datetime.now():
                num += 1
        data.append({
            "id": a.id,
            "name": a.name,
            "num_upcoming_shows": num
            })
    response["data"] = data


    # response={
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name":  "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.filter(Artist.id == artist_id).first();
    past_shows_list = []
    up_shows_list = []

    for show in artist.shows:
        if show.start_time > datetime.now():
            up_shows_list.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })
        else:
            past_shows_list.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })

    data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(', '),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": up_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(up_shows_list)
    }


    # data1={
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #       "venue_id": 1,
    #       "venue_name": "The Musical Hop",
    #       "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #       "start_time": "2019-05-21T21:30:00.000Z"
    # }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2={
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #       "venue_id": 3,
    #       "venue_name": "Park Square Live Music & Coffee",
    #       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #       "start_time": "2019-06-15T23:00:00.000Z"
    # }],
    # "upcoming_shows": [],
    # "past_shows_count": 1,
    # "upcoming_shows_count": 0,
    # }
    # data3={
    # "id": 6,
    # "name": "The Wild Sax Band",
    # "genres": ["Jazz", "Classical"],
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "432-325-5432",
    # "seeking_venue": False,
    # "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    # "past_shows": [],
    # "upcoming_shows": [{
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "start_time": "2035-04-15T20:00:00.000Z"
    # }],
    # "past_shows_count": 0,
    # "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    art = Artist.query.filter(Artist.id == artist_id).first()
    artist={
        "id": art.id,
        "name": art.name,
        "genres": art.genres.split(', '),
        "city": art.city,
        "state": art.state,
        "phone": art.phone,
        "website": art.website,
        "facebook_link": art.facebook_link,
        "seeking_venue": art.seeking_venue,
        "seeking_description": art.seeking_description,
        "image_link": art.image_link
    }

    # artist={
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    data = {
        'name': request.form['name'],
        'city': request.form['city'],
        'state': request.form['state'],
        'phone': request.form['phone'],
        'facebook_link': request.form['facebook_link'],
        'genres': ", ".join(request.form.getlist('genres')),
        'image_link': request.form['image_link'] if 'image_link' in request.form else None,
        'website': request.form['website'] if 'website' in request.form else None,
        'seeking_venue': True if request.form['seeking_venue'] == "Yes" else False,
        'seeking_description': request.form['seeking_description'] if 'seeking_description' in request.form else None

    }
    try:
        artist = Artist.query.filter(Artist.id == artist_id).first()
        arist.name = data['name'],
        artist.city = data['city'],
        artist.state = data['state'],
        artist.phone = data['phone'],
        artist.facebook_link = data['facebook_link'],
        artist.genres = data['genres'],
        artist.image_link = data['image_link'],
        artist.website = data['website'],
        artist.seeking_talent = data['seeking_talent'],
        artist.seeking_description = data['seeking_description']

        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    ven = Venue.query.filter(Venue.id == venue_id).first()
    venue={
        "id": ven.id,
        "name": ven.name,
        "genres": ven.genres.split(', '),
        "address": ven.address,
        "city": ven.city,
        "state": ven.state,
        "phone": ven.phone,
        "website": ven.website,
        "facebook_link": ven.facebook_link,
        "seeking_venue": ven.seeking_venue,
        "seeking_description": ven.seeking_description,
        "image_link": ven.image_link
    }

    # venue={
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    data = {
        'name': request.form['name'],
        'city': request.form['city'],
        'state': request.form['state'],
        'address': request.form['address'],
        'phone': request.form['phone'],
        'facebook_link': request.form['facebook_link'],
        'genres': ", ".join(request.form.getlist('genres')),
        'image_link': request.form['image_link'] if 'image_link' in request.form else None,
        'website': request.form['website'] if 'website' in request.form else None,
        'seeking_talent': True if request.form['seeking_talent'] == "Yes" else False,
        'seeking_description': request.form['seeking_description'] if 'seeking_description' in request.form else None
    }
    try:
        venue = Venue.query.filter(Venue.id == venue_id).first()
        venue.name = data['name'],
        venue.city = data['city'],
        venue.state = data['state'],
        venue.address = data['address'],
        venue.phone = data['phone'],
        venue.facebook_link = data['facebook_link'],
        venue.genres = data['genres'],
        venue.image_link = data['image_link'],
        venue.website = data['website'],
        venue.seeking_talent = data['seeking_talent'],
        venue.seeking_description = data['seeking_description']

        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    create_error = False
    query_error = False
    data = {}
    id = None
    try:
        artist = Artist(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        facebook_link = request.form['facebook_link'],
        genres = ", ".join(request.form.getlist('genres')),
        image_link = request.form['image_link'] if 'image_link' in request.form else None,
        website = request.form['website'] if 'website' in request.form else None,
        seeking_venue = True if request.form['seeking_venue'] == "Yes" else False,
        seeking_description = request.form['seeking_description'] if 'seeking_description' in request.form else None
        )
        db.session.add(artist)
        db.session.commit()
        id = artist.id
    except:
        create_error = True
        print(sys.exc_info(), d)
        db.session.rollback()
    finally:
        db.session.close()
    try:
        data = Artist.query.filter_by(id = id).first()
    except:
        print(sys.exc_info())
        query_error = True


    # on successful db insert, flash success
    if create_error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
        if query_error:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            flash('Artist ' + data.name + ' was successfully listed!')


      # on successful db insert, flash success
      # flash('Artist ' + request.form['name'] + ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    shows = Show.query.all();
    for show in shows:
        if show.start_time > datetime.now():
            data.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })

    # data=[{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        show = Show(
            venue_id = request.form['venue_id'],
            artist_id = request.form['artist_id'],
            start_time = request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()
    except:
        print(sys.exc_info())
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    # on successful db insert, flash success
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug = True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
