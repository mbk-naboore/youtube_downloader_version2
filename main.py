import os
from pytube import YouTube
import ffmpeg

ALL_POSSIBLE_RES = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
user_path = str(os.environ["HOMEPATH"].replace("\\", "/"))
main_path = f"C:{user_path}"+"/Desktop/all_youtube_downloaded_video_version_2"


print("Welcome to my YouTube downloader script.")


def making_the_youtube_object(url):
    try: 
        return YouTube(url=url)
    except Exception as ex:
        print("Sorry the url you have provided is not correct...")
def naming_the_video(ask_or_not, url):
    """ this will give the user the ability to name the video as he like..."""
    if ask_or_not and input("Would you like to use the default title [y/Y]or[n/N] ? ").lower().strip() == "n":
        # if the answer was (n) then we ask the user to give us the title he would love to have...
        return str(input("Please provide the new title :-")).strip().replace("|", "_")+".mp4"

    return making_the_youtube_object(url).title.replace("|", "_")+".mp4"


def fast_stream_progressive_true(ask_or_not, url):
    """ this function is made just to be the fastest a low-quality but fast download,
        this function will do that.by giving the streams that has the video+audio together
        and downloading that stream directly.(360p, 240p ,144p) are the expected resolutions."""
    try:
        both_streams = making_the_youtube_object(url).streams.filter(progressive=True).order_by("resolution").desc()\
            .first().download(output_path=main_path, filename=naming_the_video(ask_or_not=ask_or_not, url=url))
    except Exception as ex:
        print("There was an error while using the fast_stream_downloader function...")
        print(ex)


def best_audio_downloader(ask_or_not, url):
    try:
        if ask_or_not:  # if it is true then this is the normal one by one download , if this is false then this is the call from the bulk download so you need to name it directly by the name of the title on the youtube.... 
            audio_only = making_the_youtube_object(url).streams.filter(only_audio=True).order_by("abr").desc() \
                .first().download(output_path=main_path, filename="audio_only.mp4")
        else:
            audio_only = making_the_youtube_object(url).streams.filter(only_audio=True).order_by("abr").desc() \
                .first().download(output_path=main_path, filename=naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4")+"_(audio_only).mp4")
        return True

    except Exception as ex:
        print("There was an error while using the best_video_downloader function...")
        print(ex)
    return False
def best_video_downloader(ask_or_not, url):
    try:
        if ask_or_not:
            video_only = making_the_youtube_object(url).streams.filter(progressive=False).order_by("resolution").desc() \
                .first().download(output_path=main_path, filename="video_only.mp4")
        else:
            video_only = making_the_youtube_object(url).streams.filter(progressive=False).order_by("resolution").desc() \
                .first().download(output_path=main_path, filename=naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4")+"_(video_only).mp4")
        return True

    except Exception as ex:
        print("There was an error while using the best_audio_downloader function...")
        print(ex)
    return False
def best_stream_downloader(ask_or_not, url):
    try:
        if best_video_downloader(ask_or_not=ask_or_not, url=url) and best_audio_downloader(ask_or_not=ask_or_not, url=url):
            merging_video_and_audio(ask_or_not=ask_or_not, url=url)
            cleaning_up()

    except Exception as ex:
        print("There was an error while using the best_stream_downloader function...")
        print(ex)
    return False
def merging_video_and_audio(ask_or_not, url):
    try:
        # the merging time:
        video = ffmpeg.input(main_path+"/video_only.mp4")
        audio = ffmpeg.input(main_path+"/audio_only.mp4")
        ffmpeg.output(video, audio, main_path+"/"+naming_the_video(ask_or_not=ask_or_not, url=url),
                      vcodec='copy', acodec='aac', strict='strict').run()
    except Exception as ex:
        print("the files were not merged...")
        print(ex)
def cleaning_up():
    try:
        os.remove(main_path+"/video_only.mp4")
        os.remove(main_path+"/audio_only.mp4")
    except Exception as ex:
        print("the files were not cleaned...")
        print(ex)



def reading_url_list_from_file(file):
    try:
        if not file.endswith(".txt"):
            file = file+".txt"

        with open(file, "r") as f:
            urls_list = list()
            for line in f:
                if line.strip() and YouTube(url=line.strip()):
                    urls_list.append(line.strip())
        return urls_list
    except Exception as ex:
        print("Sorry there was an error while reading the urls from the file.")
        print(ex)
def fast_urls_textfile_downloader(urls_list):
    try:
        for url in urls_list:
            fast_stream_progressive_true(ask_or_not=False, url=url)
    except Exception as ex:
        print("Sorry there was a problem while downloading the video from the text file...")
        print(ex)    
def best_urls_textfile_downloader(urls_list):
    try:
        for url in urls_list:
            if best_video_downloader(ask_or_not=False, url=url) and best_audio_downloader(ask_or_not=False, url=url):
                bulk_merging_and_cleaning_for_best_urls_textfile_downloader(ask_or_not=False, url=url)
                pass
    except Exception as ex:
        print("Sorry there was a problem while using the best_urls_textfile_downloader function...")
        print(ex)
def bulk_merging_and_cleaning_for_best_urls_textfile_downloader(ask_or_not, url):
    try:
        # the merging time:
        video = ffmpeg.input(main_path+"/"+naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4")+"_(video_only).mp4")
        audio = ffmpeg.input(main_path+"/"+naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4")+"_(audio_only).mp4")
        ffmpeg.output(video, audio, main_path+"/"+naming_the_video(ask_or_not=ask_or_not, url=url),
                      vcodec='copy', acodec='aac', strict='strict').run()

        os.remove(main_path+"/"+naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4")+"_(video_only).mp4")
        os.remove(main_path+"/"+naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4")+"_(audio_only).mp4")
    except Exception as ex:
        print("the files were not merged...")
        print(ex)




def menu_of_available_options():

    print("Please choose the action you would like to take:")
    print("NOTE: any fast download can vary in resolution (expected resolutions 720p,480p,360p,244p,144p)...")
    print("1) fast download video+audio.")
    print("2) highest resolution video+audio.")
    print("3) highest resolution mp4 video-only.")
    print("4) clearest mp4 audio-only.")  # I might give the ability to change the type to mp3 ...
    print("5) fast download video+audio URLs from text file.")
    print("6) highest resolution video+audi URLs from text file.")

    print()
    pass

def main():
    menu_of_available_options()
    action = int(input(">>> "))
    if action in list(range(1, 5)):
        url = str(input("Please provide the URL(link) of the video: ")).strip()
        if action == 1:
            fast_stream_progressive_true(ask_or_not=True, url=url)
        elif action == 2:
            best_stream_downloader(ask_or_not=True, url=url)
        elif action == 3:
            best_video_downloader(ask_or_not=False, url=url)
        elif action == 4:
            best_audio_downloader(ask_or_not=False, url=url)
        print("\n\nThank you for using my script...@mbk-naboore")
    elif 4 < action < 7:
        if action == 5:
            fast_urls_textfile_downloader(reading_url_list_from_file(file=str(input("Please provide the path of the file that has the URLs to start the download: "))))
        elif action == 6:
            best_urls_textfile_downloader(reading_url_list_from_file(file=str(input("Please provide the path of the file that has the URLs to start the download: "))))
        print("\n\nThank you for using my script...@mbk-naboore")

    else:
        print("Sorry the action you have chosen is not correct.")


main()
