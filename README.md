# recruit 

## To build and run container

```
dzdo su
cd /home/vhaminlimk/Projects/recruit
docker build -t recruit .

# for resch4 need to use podman
docker run -d -p 3002:3000 recruit

# for interactive
sudo podman run -it -p 3001:3000 --network=host recruit

```

## To remove an index - problem with subjects table requiring ssn
```
# use \d subjects to list info on the indexes
drop index idx_764186_ssn;
```

This README would normally document whatever steps are necessary to get the
application up and running.

Things you may want to cover:

* Ruby version

* System dependencies

* Configuration

* Database creation

* Database initialization

* How to run the test suite

* Services (job queues, cache servers, search engines, etc.)

* Deployment instructions

* ...
