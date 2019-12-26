#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Reference:
# https://stackoverflow.com/questions/51812449/how-to-resume-file-download-in-python-3-5
#
# TODO:
# https://stackoverflow.com/questions/58571343/downloading-a-large-file-in-parts-using-multiple-parallel-threads
# https://stackoverflow.com/questions/33703730/adding-progress-feedback-in-grequests-task
#
import os, sys, time, datetime, re, json, random, base64, arrow

import requests, requests.utils, pickle
requests.packages.urllib3.disable_warnings()


def fetch_or_resume(url, to_file, max_retry=10, wait_sec=5, min_MB=1024):
    try:
        
        r = requests.head(url, stream=True, timeout=60)
        if not "Accept-Ranges" in r.headers:
            print("Not support Range header for resume download!"); return False
        else:
            ar = r.headers["Accept-Ranges"]
            if not ar or not "bytes" in ar:
                print("Not support Range header for resume download!"); return False

        total_size = int(r.headers.get("content-length"))
        if total_size<1024*1024*min_MB:
            print(f"[{total_size}]total_size error!"); return False

    except Exception as e:
        print(e); return False

    for retry in range(max_retry):
        time.sleep(wait_sec)
        pos = 0
        headers = {}
        with open(to_file, "ab") as f:
            pos = f.tell()
            if pos:
                if pos>=total_size:
                    break
            headers["Range"] = f"bytes={pos}-"
            with requests.get(url, stream=True, timeout=60) as r:
                if not r: break

                this_size = int(r.headers.get("content-length"))
                print(f"[{r.status_code}]<{this_size}>{r.url}")

                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)

    if pos<float(total_size):
        print(f"Download ERROR: [{retry}]retry - [{pos}]pos < [{total_size}]total")
        return False
    else:
        print(f"Download SUCCESS: [{retry}]retry -[{pos}]pos = [{total_size}]total")
        return True





