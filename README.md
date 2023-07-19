# P3-Planet-Wars-with-Behavior-Trees
*P3: Planet Wars with Behavior Trees*  
- **Team Members**
    - Zhuo Chen
    - ZeXuan Li
- **Requirements**  
  -	 -[x] Submit a behavior tree-based bot (bt_bot.py in the behavior_tree_bot directory) which successfully wins agains all of the five provided bots.  We will run it to verify that it wins.  
  -	 -[x] Submit the behaviors.py and checks.py files containing the primitive actions and checks used by your bot.  
  -	 -[x] Ensure that your bot operates within the time requirements of the game (1 second per turn).  
  -	 -[x] Submit a text file showing your behavior tree (use print(root.tree_to_string()).  
        - [click to check the behavior tree](my_behavior_tree.txt)
- **Grading Criteria**
  -  Your bot operates within the time constraint of 1 second per turn.
  -  Your bot completes each test case (individual points per test case).
  -  The winner(s) of the competition will earn extra credit.  
  
- **Modified of the Code**

  **Decorator**
  - We added decorator nodes to the code, now the bot can execute multiple strategies in one turn. This modification enables the bot to win against specific enemies in certain maps. Although the algorithm cannot achieve victory against all enemies on every map, the bot can defeat these enemies in most maps.
    
  **Defense strategy**
  - Implemented and optimized defense strategies, and now the defense strategy has reached its highest level of effectiveness. The defense strategy will deploy fleets to support or attack target planets based on the opponent's actions. Effectively, the defense strategy has significantly reduced the opponent's expansion efficiency.  
  
  **Offensive Strategy**   
  -  Various strategies have been tried, including the strongest planet attacking the weakest planet, the closest planet attacking the weakest planet, and the strongest current planet attacking the strongest planet. In the current version, the current strongest planet attacks the strongest enemy planet, which has the advantage of inflicting severe damage on the enemy fleet, and the strongest enemy planet often means high growth rates and high returns.
  
  **Spread Strategy**  
  -  Various attempts were made, and it was eventually realized that using a similar logic to the Offensive Strategy of sending a large number of fleets out would result in a lower win rate. The final logic was to find the weakest neutral planet and send ships to capture it if the capture of the sub-planet consumes no more than half the ships of the strongest planet.
