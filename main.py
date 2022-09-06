import os
from pytube import YouTube, Playlist
import ffmpeg


user_path = str(os.environ["HOMEPATH"].replace("\\", "/"))
main_path = f"C:{user_path}" + "/Desktop/all_youtube_downloaded_video_version_2"
def check_the_main_directory(folder_path):
    """ this function will check if the directory (all_youtube_downloaded_video_version_2) is
    on the desktop if not it will create that directory"""
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
        pass


def making_the_youtube_object(url):
    """ this will create the Youtube object when called using the parameter (url)..."""
    try:
        return YouTube(url=url, on_progress_callback=progress_function)
    except BaseException as ex:
        print("Sorry the url you have provided is not correct...")
def progress_function(vid, chunk, bytes_remaining):
    """ this function is called during the process of download for any vid or audio
    just to give the progress bar for the user to visualize along with some more information
    like the file size , how many MB where downloaded and how many is left..."""
    current = ((vid.filesize - bytes_remaining) / vid.filesize)  # the percent of completion...
    percent = ('{0:.1f}').format(current * 100)  # this is the % like 80%...
    progress = int(50 * current)
    status = '█' * progress + '-' * (50 - progress)
    print(
        f' ↳ |{status}| {percent}%\n   Size:{round((vid.filesize / 1024) / 1024, 1)} MB, Downloaded: {round(((vid.filesize - bytes_remaining) / 1024) / 1024, 1)} MB, Remaining:{round((bytes_remaining / 1024) / 1024, 1)} MB\n')
def naming_the_video(ask_or_not, url):
    """ this will give the user the ability to name the video as he like...and if there was
    a prohibited character in the name this will function will deal also with it..."""
    not_allowed_char = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    if ask_or_not:
        user_input = input("Would you like to use the default title [y/Y]or[n/N]? ").strip()
        print()
        while user_input.lower() != "y" and user_input.lower() != "n":
            print(f"'{user_input}'is not recognized as an accepted option.\n")
            user_input = input("Would you like to use the default title [y/Y]or[n/N]? ").strip()
            print()
            continue
        if user_input.lower() == "n":
            # if the answer was (n) then we ask the user to give us the title he would love to have...
            new_title = str(input("Please provide the new title: ")).strip()
            for i in not_allowed_char:
                new_title = new_title.replace(i, "_")
            print()
            return new_title + ".mp4"
        else:
            yt_title = making_the_youtube_object(url=url).title
            for x in not_allowed_char:
                yt_title = yt_title.replace(x, "_")
            return yt_title + ".mp4"
    else:
        yt_title = making_the_youtube_object(url=url).title
        for x in not_allowed_char:
            yt_title = yt_title.replace(x, "_")
        return yt_title + ".mp4"


def fast_stream_progressive_true(ask_or_not, url):
    """ this function is made just to be the fastest a low-quality but fast download,
        this function will do that.by giving the streams that has the video+audio together
        and downloading that stream directly.(360p, 240p ,144p) are the expected resolutions."""
    print("\nDownloading The Video:")
    try:
        """ I found that filtering and ordering the streams in this way gave me everytime the 
        best resolution available, this method of filtering was much better than most of the normal 
        ways... """

        both_streams = making_the_youtube_object(url).streams.filter(progressive=True).order_by("resolution").desc() \
            .first()
        print(f"*** The Video resolution that will be downloaded is ({both_streams.resolution}) ***\n")
        both_streams.download(output_path=main_path, filename=naming_the_video(ask_or_not=ask_or_not, url=url))
    except BaseException as ex:
        print("There was an error while downloading the video+audio.")
        print(ex)


def best_audio_downloader(ask_or_not, url):
    print("Downloading The audio-only:")
    try:
        """ if condition is True then this audio-only will be merged with a video-only, 
        so the naming system is different if that is true , just to make it easier for me 
        and for the code..."""
        if ask_or_not:
            audio_only = making_the_youtube_object(url).streams.filter(only_audio=True).order_by("abr").desc() \
                .first().download(output_path=main_path, filename="audio_only.mp4")
        else:
            audio_only = making_the_youtube_object(url).streams.filter(only_audio=True).order_by("abr").desc() \
                .first().download(output_path=main_path,filename=naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4") + "_(audio_only).mp4")
        return True

    except BaseException as ex:
        print("There was an error while downloading the audio-only.")
        print(ex)
    return False
def best_video_downloader(ask_or_not, url):
    print("\nDownloading The Video-only:")
    try:
        """ this is the same as the audio-only part , read the comment there for more info..."""
        if ask_or_not:
            video_only = making_the_youtube_object(url).streams.filter(progressive=False).order_by("resolution").desc() \
                .first()
            print(f"*** The Video resolution that will be downloaded is ({video_only.resolution}) ***\n")
            video_only.download(output_path=main_path, filename="video_only.mp4")
        else:
            video_only = making_the_youtube_object(url).streams.filter(progressive=False).order_by("resolution").desc() \
                .first().download(output_path=main_path, filename=naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4") + "_(video_only).mp4")
        return True

    except BaseException as ex:
        print("There was an error while downloading the video_only.")
        print(ex)
    return False
def best_stream_downloader(ask_or_not, url):
    try:
        """ this will make sure that both of the vid and audio is downloaded 
        if True then the merge action will be started and then the clean up after that..."""
        if best_video_downloader(ask_or_not=ask_or_not, url=url) and \
                best_audio_downloader(ask_or_not=ask_or_not, url=url):
            merging_video_and_audio(ask_or_not=ask_or_not, url=url)
            cleaning_up()

    except BaseException as ex:
        print("There was an error while downloading the video+audio.")
        print(ex)
    return False
def merging_video_and_audio(ask_or_not, url):
    """ this function is using the ffmpeg which is going to merge the vid part and audio part,
    so that will create a vid+audio mp4 file..."""
    print("\nMerging The Video and Audio streams:")
    try:
        # the merging time:
        video = ffmpeg.input(main_path + "/video_only.mp4")
        audio = ffmpeg.input(main_path + "/audio_only.mp4")
        ffmpeg.output(video, audio, main_path + "/" + naming_the_video(ask_or_not=ask_or_not, url=url),
                      vcodec='copy', acodec='aac', strict='strict').run()
    except BaseException as ex:
        print("Sorry, the video and audio streams were not merged.")
        print(ex)
def cleaning_up():
    """ this function is going to clean up the left over parts (video-only) and (audio-only)
     after they are successfully merged ..."""
    try:
        os.remove(main_path + "/video_only.mp4")
        os.remove(main_path + "/audio_only.mp4")
    except BaseException as ex:
        print("the files were not cleaned...")
        print(ex)


def check_the_urls_file(file_path):
    """ this function will take a parameter (@file_path) and will check if that file_path
    is correct and a legit file (text file) if not then will ask the user want to try and
    enter another file_path or just go back to the menu to chose another option..."""
    if not file_path.endswith(".txt"):
        file_path = file_path + ".txt"
        
    while not os.path.isfile(file_path):
        print("\nSorry, the file path you have entered is not valid.")
        y_tryagain_n_tomenu = str(input("[y/Y] to try entering the path again, [n/N] to back to main menu: ")).lower().strip()
        while y_tryagain_n_tomenu != "n" and y_tryagain_n_tomenu != "y":
            print(f"'{y_tryagain_n_tomenu}'is not recognized as an accepted option.\n")
            y_tryagain_n_tomenu = str(input("[y/Y] to try entering the path again, [n/N] to back to main menu: ")).lower().strip()
            continue  
        if y_tryagain_n_tomenu == "y":
            file_path = str(input("\nPlease provide the path of the file that has the URLs to start the download:\n>>> ")).strip()
            continue
        else:
            main()

    return file_path
def reading_url_list_from_file(file):
    """ this function will read the file and get all the Youtube video URLs only
    and return at the end a list of all the correct urls , any other thing than a Youtube
    vid will be ignored..."""
    try:
        with open(file, "r") as f:
            urls_list = list()
            for line in f:
                if line.strip() and line.startswith("https://www.youtube.com/"):
                    urls_list.append(line.strip())
        return urls_list
    except BaseException as ex:
        print("Sorry there was an error while reading the urls from the file.")
        print(ex)
def fast_urls_bulk_downloader(urls_list):
    """ will use the fast_stream_progressive_true to bulk download"""
    try:
        for url in urls_list:
            fast_stream_progressive_true(ask_or_not=False, url=url)
    except BaseException as ex:
        print("Sorry there was a problem while downloading the videos+audios from the text file...")
        print(ex)
def best_urls_bulk_downloader(urls_list):
    """ this function will use the (best_video_downloader) and (best_audio_downloader)
     to bulk download and then will bulk merge and clean up using:
      the(bulk_merging_and_cleaning_for_best_urls_textfile_downloader)"""
    try:
        for url in urls_list:
            if best_video_downloader(ask_or_not=False, url=url) and best_audio_downloader(ask_or_not=False, url=url):
                bulk_merging_and_cleaning_for_best_urls_textfile_downloader(ask_or_not=False, url=url)
                pass
    except BaseException as ex:
        print("Sorry there was a problem while downloading the videos+audios from the text file.")
        print(ex)
def best_audio_only_urls_bulk_downloader(urls_list):
    """ bulk downloading to video-only using the urls from a file..."""
    try:
        for url in urls_list:
            best_audio_downloader(ask_or_not=False, url=url)
            pass
    except BaseException as ex:
        print("Sorry there was a problem while downloading the best audios-only from the text file.")
        print(ex)
def best_video_only_urls_bulk_downloader(urls_list):
    """ bulk downloading for urls from a text file..."""
    try:
        for url in urls_list:
            best_video_downloader(ask_or_not=False, url=url)
            pass
    except BaseException as ex:
        print("Sorry there was a problem while downloading the best videos-only from the text file.")
        print(ex)
def bulk_merging_and_cleaning_for_best_urls_textfile_downloader(ask_or_not, url):
    """ this is another version of (merging_video_and_audio) and (cleaning_up) functions,
    this one is"""
    try:
        # the merging time:
        video = ffmpeg.input(
            main_path + "/" + naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4") + "_(video_only).mp4")
        audio = ffmpeg.input(
            main_path + "/" + naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4") + "_(audio_only).mp4")
        ffmpeg.output(video, audio, main_path + "/" + naming_the_video(ask_or_not=ask_or_not, url=url),
                      vcodec='copy', acodec='aac', strict='strict').run()

        # this is the cleaning part
        os.remove(
            main_path + "/" + naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4") + "_(video_only).mp4")
        os.remove(
            main_path + "/" + naming_the_video(ask_or_not=ask_or_not, url=url).strip(".mp4") + "_(audio_only).mp4")
    except BaseException as ex:
        print("Sorry, there was a problem while merging and cleaning videos+audios from the text file.")
        print(ex)


def reading_urls_from_playlist(url):
    """ this will return a urls_list as if the playlist urls is from a text file
    will work exactly the same so no need to re-do any thing..."""
    try:
        the_playlist = Playlist(url=url)
        return list(the_playlist.video_urls)
    except BaseException as ex:
        print("Sorry, there was a problem while getting URLs from the playlist.")
        print(ex)


def menu_of_available_options():
    print("\nPlease choose the action you would like to take:")
    print("******NOTE: any fast download can vary in resolution between 720p to 144p.******")
    print("1) fast download (video+audio).".title())
    print("2) highest resolution (video+audio).".title())
    print("3) highest resolution (video-only).".title())
    print("4) highest resolution (audio-only).".title())  # I might give the ability to change the type to mp3 ...
    print("5) fast download (video+audio) URLs from text file.".title())
    print("6) highest resolution (video+audi) URLs from text file.".title())
    print("7) highest resolution (video-only) URLs from text file.".title())
    print("8) highest resolution (audio-only) URLs from text file.".title())
    print("9) fast download (video+audio) playlist.".title())
    print("10) highest resolution (video+audi) playlist.".title())
    print("11) highest resolution (video-only) playlist.".title())
    print("12) highest resolution (audio-only) playlist.".title())
    print("13) to quit the script.\n".title())

    pass


def main():
    check_the_main_directory(main_path)
    menu_of_available_options()
    action = str(input(">>> ")).strip()
    if not action.isnumeric():
        print("Sorry the action you have chosen is not correct.")
        main()
    if 0 < int(action) < 5:
        url = str(input("Please provide the URL(link) of the video: ")).strip()
        if int(action) == 1:
            fast_stream_progressive_true(ask_or_not=True, url=url)
        elif int(action) == 2:
            best_stream_downloader(ask_or_not=True, url=url)
        elif int(action) == 3:
            best_video_downloader(ask_or_not=False, url=url)
        elif int(action) == 4:
            best_audio_downloader(ask_or_not=False, url=url)

    elif 4 < int(action) < 9:
        file = str(input("\nPlease provide the path of the file that has the URLs to start the download:\n>>> ")).strip()
        if int(action) == 5:
            fast_urls_bulk_downloader(reading_url_list_from_file(file=check_the_urls_file(file_path=file)))
        elif int(action) == 6:
            best_urls_bulk_downloader(reading_url_list_from_file(file=check_the_urls_file(file_path=file)))
        elif int(action) == 7:
            best_video_only_urls_bulk_downloader(reading_url_list_from_file(file=check_the_urls_file(
                file_path=file)))
        elif int(action) == 8:
            best_audio_only_urls_bulk_downloader(reading_url_list_from_file(file=check_the_urls_file(
                file_path=file)))

    elif 8 < int(action) < 13:
        url = str(input("Please provide the URL(link) of any video in the Playlist: ")).strip()
        if int(action) == 9:
            fast_urls_bulk_downloader(reading_urls_from_playlist(url=url))
        elif int(action) == 10:
            best_urls_bulk_downloader(reading_urls_from_playlist(url=url))
        elif int(action) == 10:
            best_video_only_urls_bulk_downloader(reading_urls_from_playlist(url=url))
        elif int(action) == 12:
            best_audio_only_urls_bulk_downloader(reading_urls_from_playlist(url=url))
        pass

    elif int(action) == 13:
        print("\n\nThank you for using my script...@mbk-naboore")
        exit()

    else:
        print("Sorry the action you have chosen is not correct.")
        main()
    print("\n\nThank you for using my script...@mbk-naboore")


print("\n\nWelcome to my YouTube downloader script.\n")
flag = "y"
while True:

    if flag == "y":
        main()
        flag = input("\n\nWould you like to download anything else [y/Y]or[n/N] ? ").strip().lower()
        continue

    elif flag == "n":
        break

    else:
        print(f"'{flag}'is not recognized as an accepted option.\n")
        flag = input("\n\nWould you like to download anything else [y/Y]or[n/N] ? ").strip().lower()
        continue


