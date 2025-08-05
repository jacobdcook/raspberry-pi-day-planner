# 🍓 Simple Guide - How to Use Your Day Planner

**Don't worry about all the cosmic features! Here's what you actually need to know:**

---

## 🎯 **What You Actually Need (The Basics)**

### **1. Your Daily Schedule**
The important stuff is in the `morning_tasks`, `afternoon_tasks`, and `evening_tasks` sections:

**Morning (6:45 AM - 10:30 AM):**
- 6:45 AM - Wake Up & Hydrate
- 7:00 AM - Take Supplements  
- 7:10 AM - Cold Shower
- 7:20 AM - Breakfast & Planning
- 8:00 AM - Spanish Study
- 8:45 AM - CompTIA Security+ Study
- 10:30 AM - Morning Movement

**Afternoon (11:30 AM - 4:00 PM):**
- 11:30 AM - Lunch & Hydration
- 12:15 PM - Microdose (M/W/F)
- 12:20 PM - Short Walk
- 12:30 PM - Job Search & Applications
- 2:15 PM - Afternoon Break
- 2:30 PM - Side Project Time
- 3:45 PM - Pet Care
- 4:00 PM - Core Workout

**Evening (4:30 PM - 9:00 PM):**
- 4:30 PM - Wife Time
- 5:15 PM - Dinner & Hydration
- 6:00 PM - Evening Walk
- 6:45 PM - Log & Reflect
- 7:00 PM - Free Time
- 8:15 PM - Wind-Down Routine
- 8:45 PM - Final Supplements
- 9:00 PM - Sleep Time

---

## 🔧 **How to Edit Your Schedule**

### **To Change Times:**
1. Open `config/schedule.yaml` in any text editor
2. Find the task you want to change
3. Change the `time: "XX:XX"` part
4. Save the file

### **To Add New Tasks:**
```yaml
- title: "Your New Task"
  time: "14:30"
  notes: "What you need to do"
  priority: 2
  audio_alert: true
  snooze_duration: 15
```

### **To Remove Tasks:**
Just delete the entire task block (the lines with `- title:` through `snooze_duration:`)

---

## 🎮 **Simple Controls**

### **When a Task Alert Shows:**
- **"Done"** - Mark task as completed
- **"Snooze"** - Remind me again in 15 minutes
- **Escape** - Close the alert

### **Keyboard Shortcuts:**
- **F1** - Show today's schedule
- **F2** - Show weekly overview  
- **F3** - Log your mood/energy
- **F4** - Toggle focus mode
- **F5** - Emergency break
- **F11** - Toggle fullscreen

---

## 🌐 **Web Dashboard (Optional)**

1. **Find your Pi's address:**
   ```bash
   hostname -I
   ```

2. **Open in browser:**
   ```
   http://[your-pi-address]:8000
   ```

3. **What you can do:**
   - See your schedule
   - Check completion stats
   - Test audio
   - Reload configuration

---

## 🔧 **Troubleshooting**

### **Day Planner Won't Start:**
```bash
sudo systemctl restart raspberry-pi-day-planner
```

### **Check if it's Running:**
```bash
sudo systemctl status raspberry-pi-day-planner
```

### **View Recent Logs:**
```bash
sudo journalctl -u raspberry-pi-day-planner -n 20
```

### **No Sound:**
1. Check speakers are plugged in
2. Check volume on speakers
3. Check Pi volume (speaker icon on desktop)

---

## 📊 **What Gets Tracked (Simple Version)**

- **Task completions** - Did you do your tasks?
- **Snooze counts** - How many times you hit snooze
- **Daily progress** - Overall completion rate
- **Weekly summaries** - How you did this week

---

## 🎯 **Ignore These Sections (For Now)**

You can safely ignore these complex sections:
- `legendary_mode`
- `cosmic_overdrive` 
- `omega_level`
- `alpha_omega`
- `advanced_features`
- `ai_features`
- `biohacking`
- `gamification`

**They're just for fun and don't affect your basic day planner!**

---

## 🚀 **Quick Start Checklist**

✅ **Pi is running** - Day planner starts automatically  
✅ **Monitor shows schedule** - Fullscreen display working  
✅ **Audio alerts work** - You hear the reminders  
✅ **Web dashboard accessible** - Can check from phone  
✅ **Schedule is customized** - Times match your life  

---

## 💡 **Pro Tips**

1. **Start simple** - Just use the basic schedule for now
2. **Adjust times** - Make them fit your actual routine
3. **Test the buttons** - Done, Snooze, Escape all work
4. **Check web dashboard** - Monitor from your phone
5. **Don't worry about the cosmic stuff** - It's just for fun!

---

## 🎉 **You're All Set!**

**Your day planner will:**
- ✅ **Remind you of tasks** at the right times
- ✅ **Play audio alerts** through speakers
- ✅ **Show fullscreen reminders** on monitor
- ✅ **Track your progress** automatically
- ✅ **Let you control from phone** via web dashboard

**That's it! You now have a working day planner that will help you stay on schedule!** 🚀

---

## 🤔 **Need to Change Something?**

**To edit your schedule:**
```bash
nano config/schedule.yaml
```

**To restart the service:**
```bash
sudo systemctl restart raspberry-pi-day-planner
```

**To check if it's working:**
```bash
sudo systemctl status raspberry-pi-day-planner
```

**That's all you need to know! The cosmic features are just bonus fun - your day planner works perfectly without them!** 😊 