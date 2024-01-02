from bot import discord, bot, commands, pymongo, traceback
from constants import TOKEN, LINK, GUILD_ID
from data import IGCSE_SUBJECT_CODES, ALEVEL_SUBJECT_CODES, alevelsubjects, igsubjects
import random
import pyshorteners


@bot.slash_command(name="random_pyp", description="gets a random CAIE past year paper.")
async def random_pyp(interaction: discord.Interaction, 
                     programme: str = discord.SlashOption(name="directories", description= "IGCSE or ALEVELS?", choices=["A-Level", "IGCSE"], required=True),
                     subject_code: str = discord.SlashOption(name="subject_code", description="please enter the subject code", required=True),
                     paper_number: str = discord.SlashOption(name="paper_no", description= "Enter a paper number", required=True)):
      
      #PAPER_INFORMATION
      insert_codes = ["0410", "0445", "0448", "0449", "0450", "0454", "0457", "0460", "0471", "0500", "0501", "0502", "0503", "0504", "0505", "0508", "0509", "0513", "0514", "0516", "0518", "0538", "9609"]
      YEARS = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
      LAT_SES = ["m", "s"]
      PAPER_VARIENT = ["1", "2", "3"]
      SESSIONS = ["s", "w", "m"]      

      #USAGE OF THE RANDOM VARIABLE
      ranyear = random.choice(YEARS)
      ranvar = random.choice(PAPER_VARIENT)
      ranses = random.choice(SESSIONS)
      ses = random.choice(LAT_SES)
      in_validation = insert_codes.__contains__(subject_code)
      sesh = ""

      if programme == "IGCSE":
            pc_valication = len(paper_number)
            subject_name = igsubjects.get(subject_code)
            ig_validation = IGCSE_SUBJECT_CODES.__contains__(subject_code)
            if ig_validation == True:
                  if pc_valication == 1:
                        if paper_number < "6":
                              if in_validation == True:
                                    if ranyear <= "2017":
                                          if ranses == "s":
                                                sesh = "Jun"
                                          elif ranses == "w":
                                                sesh = "Nov"
                                          else:
                                                sesh = "Mar"
                                                ranvar = "2"
                                          
                                          qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                          inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)

                                    elif ranyear == "2018" or "2019" or "2020" or "2021":
                                          if ranses == "s":
                                                sesh = "May-June"
                                          elif ranses == "w":
                                                sesh = "Oct-Nov"
                                          else:
                                                sesh = "March"
                                                ranvar = "2"
                                          qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                          inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)

                                    elif ranyear == "2023":
                                          if ses == "s":
                                                sesh = "May-June"
                                          else:
                                                sesh = "March"
                                                ranvar = "2"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                          inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)

                                    else:
                                          if ranses == "s":
                                                sesh = "May-June"
                                          elif ranses == "w":
                                                sesh = "Oct-Nov"
                                          else:
                                                sesh = "Feb-March"
                                          qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                          inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)
                              else:
                                    if ranyear <= "2017":
                                          if ranses == "s":
                                                sesh = "Jun"
                                          elif ranses == "w":
                                                sesh = "Nov"
                                          else:
                                                sesh = "Mar"
                                                ranvar = "2"
                                          
                                          qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)

                                    elif ranyear == "2018" or "2019" or "2020" or "2021":
                                          if ranses == "s":
                                                sesh = "May-June"
                                          elif ranses == "w":
                                                sesh = "Oct-Nov"
                                          else:
                                                sesh = "March"
                                                ranvar = "2"
                                          qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)

                                    elif ranyear == "2023":
                                          if ses == "s":
                                                sesh = "May-June"
                                          else:
                                                sesh = "March"
                                                ranvar = "2"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)
                                    
                                    else:
                                          if ranses == "s":
                                                sesh = "May-June"
                                          elif ranses == "w":
                                                sesh = "Oct-Nov"
                                          else:
                                                sesh = "Feb-March"
                                          qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                          qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                          msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                          embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                          await interaction.send(embed=embed)
                        else:
                              await interaction.send("Invalid Paper Number. Please Try again.", ephemeral=True)
                  else:
                        await interaction.send("Invalid Paper Number. Please Try again.", ephemeral=True)
            else:
                  await interaction.send("Invalid Subject Code. Please Try again.", ephemeral=True)
      else:
            subject_name = alevelsubjects.get(subject_code)
            al_validation = ALEVEL_SUBJECT_CODES.__contains__(subject_code)
            if al_validation == True:
                  if in_validation == True:
                        if ranyear <= "2017":
                              if ranses == "s":
                                    sesh = "Jun"
                              elif ranses == "w":
                                    sesh = "Nov"
                              else:
                                    sesh = "Mar"
                                    ranvar = "2"
                              
                              qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)

                        elif ranyear == "2018" or "2019" or "2020" or "2021":
                              if ranses == "s":
                                    sesh = "May-June"
                              elif ranses == "w":
                                    sesh = "Oct-Nov"
                              else:
                                    sesh = "March"
                                    ranvar = "2"
                              qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                              inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)

                        elif ranyear == "2023":
                              if ses == "s":
                                    sesh = "May-June"
                              else:
                                    sesh = "March"
                                    ranvar = "2"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                              inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)
                        
                        else:
                              if ranses == "s":
                                    sesh = "May-June"
                              elif ranses == "w":
                                    sesh = "Oct-Nov"
                              else:
                                    sesh = "Feb-March"
                              qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                              inurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)
                  else:
                        if ranyear <= "2017":
                              if ranses == "s":
                                    sesh = "Jun"
                              elif ranses == "w":
                                    sesh = "Nov"
                              else:
                                    sesh = "Mar"
                                    ranvar = "2"
                              
                              qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}/20{ranyear[2:5]}%20{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)

                        elif ranyear == "2018" or "2019" or "2020" or "2021":
                              if ranses == "s":
                                    sesh = "May-June"
                              elif ranses == "w":
                                    sesh = "Oct-Nov"
                              else:
                                    sesh = "March"
                                    ranvar = "2"
                              qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)

                        elif ranyear == "2023":
                              if ses == "s":
                                    sesh = "May-June"
                              else:
                                    sesh = "March"
                                    ranvar = "2"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)
                        
                        else:
                              if ranses == "s":
                                    sesh = "May-June"
                              elif ranses == "w":
                                    sesh = "Oct-Nov"
                              else:
                                    sesh = "Feb-March"
                              qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                              qpurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                              msurl = pyshorteners.Shortener().tinyurl.short(f"https://pastpapers.co/cie/{programme}/{subject_name}-{subject_code}/{ranyear}-{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                              embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                              await interaction.send(embed=embed)

            else:
                  await interaction.send("Invalid Subject Code. Please Try again.", ephemeral=True)
