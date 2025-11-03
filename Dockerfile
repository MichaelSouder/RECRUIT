FROM ruby:3.0.0

# throw errors if Gemfile has been modified since Gemfile.lock
# RUN bundle config --global frozen 1

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


RUN apt-get update && apt-get install -y nodejs --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y  postgresql-client sqlite3 --no-install-recommends && rm -rf /var/lib/apt/lists/*

# update CA certificates - man in the middle attack error on bundle install
# solution was to turn off https in Gemfile to avoid cert error
#RUN apt-get install ca-certificates -y
#RUN gem update --system

ENV RAILS_ENV production
ENV RAILS_SERVE_STATIC_FILES true
ENV RAILS_LOG_TO_STDOUT true

COPY Gemfile /usr/src/app/

# Uncomment the line below if Gemfile.lock is maintained outside of build process
COPY Gemfile.lock /usr/src/app/


RUN bundle install 

COPY . /usr/src/app
#RUN bundle exec rake assets:precompile

EXPOSE 3000
CMD ["rails", "server", "-b", "0.0.0.0"]
#CMD ["rails", "server", "-b", "10.104.8.68"]
