# Just Another RSS Reader

Is just a try at reading rss from predominantly news websites and storing them. The only difference is the short ML article summarizer that lets you know the context quickly.

## Design

The main components are bound to be run separately.
In its essence the project only has a reader/writer job and then a starlette powered tailwind designed frontend.

### Collect

The main task of this job is to read rss feeds configured asynchronously and then pass it through a summarizer and store it

### Web App

Picks the newly stored article feeds from the storage and paginates and shows it. Its that simple

### Hosting

This needs a mention here. Because at the end of the day Im using this as my personal news source gatherer.
Also it is my experiment to see how much I can achieve without spending a lot of money.

- The Job is run via Github Actions schedule
- Database is on the Supabase Free tier.
- The webapp runs on render which gives me a free onrender.com domain.
