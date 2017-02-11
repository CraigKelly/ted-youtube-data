-- Note that we use the edist function - it is defined and added in tosqlite.py
create table matching_speakers (ted_id, youtube_id, headline_dist, ted_headline, yt_headline, ted_speaker, yt_speaker);

insert into matching_speakers
     select t.ted_id 'ted_id',
            y.youtube_id 'youtube_id',
            edist(t.headline, y.headline) 'headline_dist',
            t.headline 'ted_headline',
            y.headline 'yt_headline',
            t.speaker 'ted_speaker',
            y.speaker 'yt_speaker'
       from ted t
 inner join ted y
         on t.speaker = y.speaker
      where t.ted_id != '' and t.youtube_id == ''
        and y.ted_id == '' and y.youtube_id != ''
;
