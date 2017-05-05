# SplitStalker
  ## Synopsis
  SplitStalker is a simple tool allowing users to to follow collegiate athletes competing in track and field.

## How it works
  SplitStalker uses the Django backened for simple storing of Athletes as well as Users. Athletes are defined by a first name, last name, and school. Users may follow one or more athletes.
  
  The program meetPing_lowbandwidth.py is run on scheduele depending on the day of the week in order to scrape collegiate times from across the web. It will then compare the athletes from various meet results to the athletes users are following, account for small variations in spelling, and send emails to the users notifying them of their followed athlete's times.
