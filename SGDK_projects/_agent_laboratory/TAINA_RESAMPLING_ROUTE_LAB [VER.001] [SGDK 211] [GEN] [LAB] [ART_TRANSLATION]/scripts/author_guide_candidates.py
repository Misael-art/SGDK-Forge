#!/usr/bin/env python3
"""Author two explicitly hand-planned native-grid guide candidates.

The plans are independent pixel strokes written for this lab.  They do not
read or copy pixels from v01-v04 or from any resampling output.
"""
import argparse, hashlib, json, time
from pathlib import Path
from PIL import Image

PALETTE=[(0,0,0),(34,0,0),(34,0,34),(68,34,68),(102,68,34),(136,68,34),(170,102,34),(204,136,68),(204,68,0),(238,102,0),(238,136,68),(0,68,68),(0,136,136),(0,170,170),(0,0,68),(34,34,102)]
COLORS={"o":1,"h":2,"m":3,"k":4,"d":5,"s":6,"l":7,"r":8,"t":9,"u":10,"q":11,"w":12,"v":13,"n":14,"i":15}

def plan_a():
    S=[]
    def r(y,a,b,c): S.append([y,a,b,c])
    for y,a,b,c in [(3,23,31,'o'),(4,19,34,'o'),(5,16,36,'o'),(6,14,38,'o'),(7,13,39,'o'),(8,12,40,'o'),(9,12,40,'o'),(10,13,39,'o'),(11,14,39,'o'),(12,15,38,'o'),(13,16,37,'o'),(14,17,36,'o'),(15,18,35,'o')]: r(y,a,b,c)
    for y,a,b,c in [(4,13,20,'h'),(5,12,22,'h'),(6,11,22,'m'),(7,10,20,'m'),(8,11,19,'m'),(9,12,18,'k'),(10,13,18,'m'),(11,14,19,'h'),(12,15,20,'h'),(13,16,21,'k'),(14,17,22,'m'),(15,18,23,'h')]: r(y,a,b,c)
    for y,a,b,c in [(8,24,37,'d'),(9,23,38,'s'),(10,23,38,'s'),(11,24,38,'s'),(12,24,38,'s'),(13,24,37,'s'),(14,25,36,'s'),(15,26,35,'s'),(16,27,34,'s'),(17,28,34,'s'),(18,28,33,'s'),(19,29,34,'s'),(20,28,35,'o')]: r(y,a,b,c)
    r(11,33,35,'o'); r(12,33,36,'o'); r(13,35,37,'d'); r(14,35,37,'d'); r(17,27,29,'o'); r(18,27,29,'o')
    for y,a,b,c in [(18,26,31,'d'),(19,25,32,'d'),(20,24,33,'d'),(21,22,35,'o'),(22,20,37,'o'),(23,18,39,'o'),(24,17,40,'o'),(25,16,41,'o'),(26,16,41,'o'),(27,17,40,'o'),(28,18,39,'o'),(29,19,38,'o'),(30,20,37,'o'),(31,21,36,'o'),(32,22,35,'o'),(33,23,34,'o')]: r(y,a,b,c)
    for y,a,b,c in [(19,28,31,'s'),(20,25,34,'s'),(21,23,36,'s'),(22,22,37,'s'),(23,21,38,'s'),(24,21,38,'s'),(25,22,37,'s'),(26,23,36,'s'),(27,24,35,'s'),(28,25,34,'s'),(29,25,34,'s'),(30,26,33,'s'),(31,26,33,'s'),(32,27,32,'s'),(33,27,32,'s')]: r(y,a,b,c)
    for y,a,b,c in [(22,17,22,'o'),(23,15,21,'o'),(24,14,20,'o'),(25,13,19,'o'),(26,12,18,'o'),(27,11,17,'o'),(28,10,16,'o'),(29,10,16,'o'),(30,11,17,'o'),(31,12,18,'o'),(32,13,19,'o'),(33,14,20,'o'),(34,15,21,'o')]: r(y,a,b,c)
    for y,a,b,c in [(22,18,22,'q'),(23,16,21,'q'),(24,15,20,'w'),(25,14,19,'w'),(26,13,18,'w'),(27,12,17,'v'),(28,11,16,'v'),(29,11,16,'w'),(30,12,17,'w'),(31,13,18,'q'),(32,14,19,'q'),(33,15,20,'w')]: r(y,a,b,c)
    for y,a,b,c in [(22,37,42,'o'),(23,38,44,'o'),(24,39,45,'o'),(25,40,46,'o'),(26,41,47,'o'),(27,42,48,'o'),(28,42,49,'o'),(29,42,49,'o'),(30,41,48,'o'),(31,40,47,'o'),(32,39,46,'o'),(33,38,45,'o'),(34,37,44,'o')]: r(y,a,b,c)
    for y,a,b,c in [(22,37,40,'q'),(23,38,42,'q'),(24,39,43,'w'),(25,40,44,'w'),(26,41,45,'v'),(27,42,46,'v'),(28,43,47,'w'),(29,43,47,'w'),(30,42,46,'q'),(31,41,45,'q'),(32,40,44,'w'),(33,39,43,'w')]: r(y,a,b,c)
    for y,a,b,c in [(34,22,35,'s'),(35,22,35,'s'),(36,21,36,'s'),(37,21,36,'s'),(38,22,35,'s'),(39,23,34,'s'),(40,23,34,'s'),(41,24,33,'s'),(42,24,33,'s'),(43,25,32,'s')]: r(y,a,b,c)
    for y,a,b,c in [(42,16,41,'o'),(43,15,42,'o'),(44,14,43,'o'),(45,14,43,'o'),(46,15,42,'o'),(47,16,41,'o'),(48,17,40,'o'),(49,18,39,'o')]: r(y,a,b,c)
    for y,a,b,c in [(43,17,40,'q'),(44,16,41,'w'),(45,15,42,'w'),(46,16,41,'v'),(47,17,40,'w'),(48,18,39,'q'),(49,19,38,'w'),(50,35,43,'q'),(51,37,45,'w'),(52,39,47,'w'),(53,40,48,'v'),(54,41,48,'w'),(55,42,48,'q'),(56,43,47,'w'),(57,44,46,'w'),(58,45,47,'v'),(59,44,47,'w'),(60,43,46,'q'),(61,42,45,'w'),(62,41,44,'w')]: r(y,a,b,c)
    for y,a,b,c in [(50,19,27,'o'),(51,18,28,'o'),(52,17,29,'o'),(53,16,29,'o'),(54,15,29,'o'),(55,14,29,'o'),(56,13,28,'o'),(57,12,28,'o'),(58,11,27,'o'),(59,10,27,'o'),(60,10,26,'o'),(61,9,26,'o'),(62,9,25,'o'),(63,10,25,'o'),(64,11,25,'o'),(65,12,25,'o'),(66,13,25,'o'),(67,14,25,'o'),(68,15,25,'o'),(69,16,25,'o')]: r(y,a,b,c)
    for y,a,b,c in [(50,20,27,'i'),(51,19,28,'i'),(52,18,28,'i'),(53,17,28,'i'),(54,16,28,'i'),(55,15,28,'i'),(56,14,27,'i'),(57,13,27,'n'),(58,12,26,'n'),(59,11,26,'n'),(60,11,25,'i'),(61,10,25,'i'),(62,10,24,'n'),(63,11,24,'n'),(64,12,24,'i'),(65,13,24,'i'),(66,14,24,'n'),(67,15,24,'n'),(68,16,24,'i')]: r(y,a,b,c)
    for y,a,b,c in [(50,29,38,'o'),(51,29,39,'o'),(52,29,40,'o'),(53,29,41,'o'),(54,29,42,'o'),(55,29,42,'o'),(56,29,43,'o'),(57,29,43,'o'),(58,29,44,'o'),(59,29,44,'o'),(60,29,44,'o'),(61,30,44,'o'),(62,30,44,'o'),(63,30,43,'o'),(64,30,43,'o'),(65,30,42,'o'),(66,30,42,'o'),(67,30,41,'o'),(68,30,40,'o'),(69,30,39,'o')]: r(y,a,b,c)
    for y,a,b,c in [(50,30,38,'i'),(51,30,39,'i'),(52,30,40,'i'),(53,30,40,'i'),(54,30,41,'i'),(55,30,41,'i'),(56,30,42,'n'),(57,30,42,'n'),(58,30,43,'i'),(59,30,43,'i'),(60,30,43,'n'),(61,31,43,'n'),(62,31,43,'i'),(63,31,42,'i'),(64,31,42,'n'),(65,31,41,'n'),(66,31,41,'i'),(67,31,40,'i'),(68,31,39,'n')]: r(y,a,b,c)
    for y,a,b,c in [(68,13,26,'o'),(69,12,27,'o'),(70,12,27,'o'),(71,13,28,'o'),(72,14,29,'o'),(73,15,30,'o'),(74,16,30,'o'),(75,17,29,'o'),(76,18,28,'o'),(77,18,27,'o')]: r(y,a,b,c)
    for y,a,b,c in [(68,15,25,'d'),(69,14,26,'d'),(70,14,26,'s'),(71,15,27,'s'),(72,16,28,'s'),(73,17,29,'s'),(74,18,29,'s'),(75,19,28,'s'),(76,20,27,'s')]: r(y,a,b,c)
    for y,a,b,c in [(68,30,42,'o'),(69,30,43,'o'),(70,30,44,'o'),(71,31,45,'o'),(72,32,46,'o'),(73,33,47,'o'),(74,34,48,'o'),(75,35,49,'o'),(76,36,50,'o'),(77,37,51,'o')]: r(y,a,b,c)
    for y,a,b,c in [(68,31,41,'d'),(69,31,42,'d'),(70,31,43,'s'),(71,32,44,'s'),(72,33,45,'s'),(73,34,46,'s'),(74,35,47,'s'),(75,36,48,'s'),(76,37,49,'s')]: r(y,a,b,c)
    return S

def plan_b():
    s=plan_a()
    # Causal alternative: alter only native clusters for face, shoulders, guard
    # and base.  These are explicit authoring strokes, not copied pixels.
    s += [[12,30,32,'o'],[13,30,34,'o'],[14,31,35,'d'],[15,31,34,'s'],[16,30,33,'s'],[17,29,32,'s'],[18,28,32,'o'],[19,27,33,'s'],[20,26,34,'s'],[21,25,35,'o'],[22,24,36,'s'],[23,23,37,'s'],[24,23,37,'s'],[25,24,36,'s'],[26,25,35,'s'],[27,26,34,'s'],[28,27,33,'s'],[29,28,32,'s'],[30,29,32,'s'],[31,29,31,'o'],[32,29,32,'o'],[18,22,25,'o'],[19,21,25,'o'],[20,20,25,'o'],[21,19,25,'o'],[22,18,24,'q'],[23,17,24,'q'],[24,16,23,'w'],[25,15,22,'w'],[26,14,21,'v'],[27,13,20,'v'],[28,12,19,'w'],[29,12,19,'w'],[30,13,20,'q'],[31,14,21,'q'],[32,15,22,'w'],[33,16,23,'w'],[18,35,39,'o'],[19,36,40,'o'],[20,37,41,'o'],[21,38,42,'o'],[22,39,43,'q'],[23,40,44,'q'],[24,41,45,'w'],[25,42,46,'w'],[26,43,47,'v'],[27,44,48,'v'],[28,44,49,'w'],[29,44,49,'w'],[30,43,48,'q'],[31,42,47,'q'],[32,41,46,'w'],[33,40,45,'w'],[45,12,44,'o'],[46,13,43,'q'],[47,14,42,'w'],[48,15,41,'v'],[49,16,40,'w'],[50,17,39,'q'],[51,18,38,'w'],[52,19,37,'q'],[53,20,36,'w'],[54,21,35,'q'],[55,22,34,'w'],[56,23,33,'q'],[57,24,32,'w'],[58,25,31,'q'],[59,26,30,'w'],[60,27,29,'q'],[61,28,36,'w'],[62,29,37,'v'],[63,30,38,'w'],[64,31,39,'q']]
    return s

def write_candidate(lab, name, strokes):
    grid=[0]*4480; actions=[]; n=0; started=time.perf_counter()
    for y,x0,x1,color in strokes:
        for x in range(x0,x1+1):
            if not (0<=x<56 and 0<=y<80): continue
            idx=COLORS[color]; pos=y*56+x; before=grid[pos]; grid[pos]=idx; n+=1; actions.append({"n":n,"kind":"pencil","x":x,"y":y,"color_index":idx,"before":before,"after":idx})
    out=lab/"rework_candidates"/name; out.mkdir(parents=True,exist_ok=True); p=out/(name+".png"); im=Image.new("P",(56,80),0); im.putpalette(sum((list(v) for v in PALETTE),[])+[0,0,0]*240); im.putdata(grid); im.save(p,"PNG",bits=4,transparency=0)
    log={"schema_version":"native_authoring_guide_action_log.v1","asset_id":name,"canvas":{"width":56,"height":80,"pivot":[28,74],"grid":8},"method":"native_grid_manual_reauthoring_from_geometry_guide","source_pixels_copied":False,"source_role":"raw_geometry_probe_as_anatomical_guide_only","actions":actions,"elapsed_seconds":round(time.perf_counter()-started,6),"claim_ceiling":"native_authoring_guide_candidate","human_approval":"pending"}; lp=out/(name+".actions.json"); lp.write_text(json.dumps(log,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"asset_id":name,"path":str(p.relative_to(lab)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"action_log":str(lp.relative_to(lab)),"action_log_sha256":hashlib.sha256(lp.read_bytes()).hexdigest(),"actions":len(actions),"elapsed_seconds":log["elapsed_seconds"],"regions_altered":["face_eye","shoulder_arm_attachment","diagonal_guard","torso_hip","legs_feet","sash"],"landmarks_recovered":["hair_top_and_width","head_center","shoulders","wrists","waist","ground_line"],"landmarks_still_ambiguous":["eye_line","chin","elbows","hip_left_right","knees","balance_axis","guard_action_line"],"material_failures":["native_guide_palette_is_directional_only; requires later material topology review"],"visual_difference":"independent manual native-grid guide; not a pixel derivative of v01-v04 or a resampling probe"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--lab-root",type=Path,required=True); args=ap.parse_args(); lab=args.lab_root.resolve(); rows=[write_candidate(lab,"native_guide_candidate_route_a_v01",plan_a()),write_candidate(lab,"native_guide_candidate_route_b_v01",plan_b())]; (lab/"cleanup_cost_report.json").write_text(json.dumps({"schema_version":"cleanup_cost_report.v1","status":"guide_candidates_only","routes":rows,"selection_limit":2,"v04_source_pixels_used":False,"not_v05":True,"notes":"Costs are authoring-action counts and elapsed wall time, not an aesthetic score; both guides require human review and remain forbidden in res/."},indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps(rows,ensure_ascii=False))
if __name__=="__main__": main()
