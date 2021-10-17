from flask import Flask, render_template, request, redirect, url_for
from .models import Data_Hold, db, User, Tweet
from .twitter import get_user_info, get_tweets
from .nlp_modeling import convert_word2vec, make_prediction
import os, numpy as np
from datetime import date


def create_app():

    '''
    This function defines all application processes. Subprocesses are
    imported from individual .py files. All dependencies are outlined
    in the pipfile.lock. Commends are added where deemed necessary for
    clarity.
    '''

    # Initialize flask and sqlalchemy params
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.secret_key = os.getenv("APP_SECRET_KEY")

    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET", "POST"])
    def main():

        '''
        Landing page of application. Houses name inputs for the app that
        facilitate the population of data for analysis and prediction.
        '''

        screen_name = request.form.get("screen_name")
        id_u = request.form.get("id_u")
        id_d = request.form.get("id_d")
        Data_Hold.query.delete()
        db.session.commit()

        # If name submitted, define all values for class creations
        if screen_name:
            # Use screen name to get basic user info
            user_id, screen_name = get_user_info(screen_name)
            
            # Collect data from recent tweets and extract
            tweet_dict = get_tweets(user_id)
            tweet_vectors = [] # Empty list to append during for loop
            for i in tweet_dict:
                tweet_id = i['tweet_id']
                tweet_text = i['tweet_text']
                text_vector = convert_word2vec(tweet_text)
                tweet_vectors.append(text_vector) # Append to big array
                # Use collected and processed data to create and
                # add Tweet class to database
                tweet = Tweet(
                    id=tweet_id,
                    body=tweet_text,
                    tweet_vect=text_vector,
                    user_id=user_id,
                    last_updated=date.today())
                db.session.add(tweet)
            user = User(
                id=user_id,
                screen_name=screen_name,
                last_updated=date.today(),
                tweet_vectors=np.array(tweet_vectors)
                )
            db.session.add(user)

            db.session.commit()

        if id_d:
            # Remove user data
            user = User.query.where(User.id == id_d).one()
            db.session.delete(user)
            db.session.commit()

        if id_u:
            # Remove old user data
            user = User.query.where(User.id == id_u).one()
            screen_name = user.screen_name
            db.session.delete(user)

            # Use screen name to get basic user info
            user_id, screen_name = get_user_info(screen_name)
            
            # Collect data from recent tweets and extract
            tweet_dict = get_tweets(user_id)
            tweet_vectors = [] # Empty list to append during for loop
            for i in tweet_dict:
                tweet_id = i['tweet_id']
                tweet_text = i['tweet_text']
                text_vector = convert_word2vec(tweet_text)
                tweet_vectors.append(text_vector) # Append to big array
                # Use collected and processed data to create and
                # add Tweet class to database
                tweet = Tweet(
                    id=tweet_id,
                    body=tweet_text,
                    tweet_vect=text_vector,
                    user_id=user_id,
                    last_updated=date.today())
                db.session.add(tweet)
            user = User(
                id=user_id,
                screen_name=screen_name,
                last_updated=date.today(),
                tweet_vectors=np.array(tweet_vectors)
                )
            db.session.add(user)

            db.session.commit()
        
        # Define variables and return html rendering
        users = User.query.all()       
        tweets = Tweet.query.all()

        return render_template("home.html", users=users, tweets=tweets)

    @app.route('/about')
    def about():

        '''
        A quick description page of the application.
        '''
        return render_template("about.html")

    @app.route('/refresh')
    def refresh_db():

        '''
        A simple route that deletes the database, used for testing.
        '''

        db.drop_all()
        db.create_all()
        return 'Database Refreshed'

    @app.route('/enter_first', methods=["GET", "POST"])
    def enter_first_screen_name():

        '''
        Page to enter first screen name in.
        '''
        name1 = request.form.get("name1")
        if name1:
            error = "That user has not been added to the database yet."
            user1 = User.query.filter_by(
                screen_name=name1
                ).first_or_404(description=error)
            id_1 = user1.id
            data = Data_Hold(id_1=id_1)
            db.session.add(data)
            db.session.commit()
            return redirect("/enter_second")

        return render_template("enter_first.html")
        
    @app.route('/enter_second', methods=["GET", "POST"])
    def enter_second_screen_name():

        '''
        Page to enter second screen name in.
        '''
        name2 = request.form.get("name2")
        if name2:
            error = "That user has not been added to the database yet."
            user2 = User.query.filter_by(
                screen_name=name2
                ).first_or_404(description=error)
            data = Data_Hold.query.first()
            id_1 = data.id_1
            id_2 = user2.id
            db.session.delete(data)
            data = Data_Hold(id_1=id_1, id_2=id_2)
            db.session.add(data)
            db.session.commit()
            return redirect("/enter_tweet")

        return render_template("enter_second.html")

    @app.route('/enter_tweet', methods=["GET", "POST"])
    def enter_hypothetical_tweet():

        '''
        Page to enter hypothetical tweet that the logistic regression
        classifier will use as its y variable.
        '''

        hypo_tweet = request.form.get("hypo_tweet")
        if hypo_tweet:
            data = Data_Hold.query.first()
            id_1 = data.id_1
            id_2 = data.id_2
            db.session.delete(data)
            data = Data_Hold(id_1=id_1, id_2=id_2, hypo_tweet=hypo_tweet)
            db.session.add(data)
            db.session.commit()
            return redirect("/results")

        return render_template("enter_tweet.html")

    @app.route('/results', methods=["GET", "POST"])
    def clf_prediction():

        '''
        This route returns the prediction created by the logistic
        regression algorithm using the vectorized tweets based on
        the usernames given.
        '''

        data = Data_Hold.query.first()
        id_1 = data.id_1
        id_2 = data.id_2
        name1 = User.query.get(id_1)
        name2 = User.query.get(id_2)
        hypo_tweet = data.hypo_tweet
        X_predict = convert_word2vec(hypo_tweet).reshape(1, -1)
        guess = make_prediction(id_1, id_2, X_predict)
        if guess == 0:
            guess = name1
        if guess == 1:
            guess = name2

        return render_template("results.html", guess=guess,name1=name1, name2=name2, hypo_tweet=hypo_tweet)

    return app