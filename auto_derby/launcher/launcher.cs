using Microsoft.Win32;
using System.Collections.ObjectModel;
using System.ComponentModel;

namespace NateScarlet.AutoDerby
{
    public class JobOption
    {
        public string Label
        { get; set; }

        public string Value
        { get; set; }
    }

    public class JobOptions : ObservableCollection<JobOption>
    {
        public JobOptions()
        {
            Add(new JobOption()
            {
                Label = "Nurturing",
                Value = "nurturing",
            });
            Add(new JobOption()
            {
                Label = "Champions meeting",
                Value = "champions_meeting",
            });
            Add(new JobOption()
            {
                Label = "Team race",
                Value = "team_race",
            });
            Add(new JobOption()
            {
                Label = "Daily race: Money",
                Value = "daily_race_money",
            });
            Add(new JobOption()
            {
                Label = "Daily race: SP",
                Value = "daily_race_sp",
            });
            Add(new JobOption()
            {
                Label = "Legend race",
                Value = "legend_race",
            });
            Add(new JobOption()
            {
                Label = "Roulette derby",
                Value = "roulette_derby",
            });
        }
    }

    public class DataContext : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;
        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChangedEventHandler handler = PropertyChanged;
            if (handler != null) handler(this, new PropertyChangedEventArgs(propertyName));
        }

        private const string RegistryPath = @"Software\NateScarlet\auto-derby";

        private RegistryKey key;

        public DataContext()
        {
            this.key = Registry.CurrentUser.OpenSubKey(RegistryPath, true);
            if (this.key == null)
            {
                this.key = Registry.CurrentUser.CreateSubKey(RegistryPath);
            }

            this.JobOptions1 = new JobOptions();
        }
        ~DataContext()
        {
            key.Dispose();
        }

        public string DefaultSingleModeChoicesDataPath;
        public string SingleModeChoicesDataPath
        {
            get
            {
                return (string)key.GetValue("SingleModeChoicesDataPath", DefaultSingleModeChoicesDataPath);
            }
            set
            {
                key.SetValue("SingleModeChoicesDataPath", value);
                OnPropertyChanged("SingleModeChoicesDataPath");
            }
        }

        public string DefaultPythonExecutablePath;
        public string PythonExecutablePath
        {
            get
            {
                return (string)key.GetValue("PythonExecutablePath", DefaultPythonExecutablePath);
            }
            set
            {
                key.SetValue("PythonExecutablePath", value);
                OnPropertyChanged("PythonExecutablePath");
            }
        }

        public int PauseIfRaceOrderGt
        {
            get
            {
                return (int)key.GetValue("PauseIfRaceOrderGt", 5);
            }
            set
            {
                key.SetValue("PauseIfRaceOrderGt", value, RegistryValueKind.DWord);
                OnPropertyChanged("PauseIfRaceOrderGt");
            }
        }

        public string Plugins
        {
            get
            {
                return (string)key.GetValue("Plugins", "");
            }
            set
            {
                key.SetValue("Plugins", value);
                OnPropertyChanged("Plugins");
            }
        }

        public string TargetTrainingLevels
        {
            get
            {
                return (string)key.GetValue("TargetTrainingLevels", "5,3,3,0,");
            }
            set
            {
                key.SetValue("TargetTrainingLevels", value);
                OnPropertyChanged("TargetTrainingLevels");
            }
        }

        public string ADBAddress
        {
            get
            {
                return (string)key.GetValue("ADBAddress", "");
            }
            set
            {
                key.SetValue("ADBAddress", value);
                OnPropertyChanged("ADBAddress");
            }
        }

        public bool Debug
        {
            get
            {
                return (int)key.GetValue("Debug", 1) != 0;
            }
            set
            {
                key.SetValue("Debug", value, RegistryValueKind.DWord);
                OnPropertyChanged("Debug");
            }
        }

        public bool CheckUpdate
        {
            get
            {
                return (int)key.GetValue("CheckUpdate", 1) != 0;
            }
            set
            {
                key.SetValue("CheckUpdate", value, RegistryValueKind.DWord);
                OnPropertyChanged("CheckUpdate");
            }
        }


        public string Job
        {
            get
            {
                return (string)key.GetValue("Job", "nurturing");
            }
            set
            {
                key.SetValue("Job", value);
                OnPropertyChanged("Job");
            }
        }

        public JobOptions JobOptions1
        { get; set; }
    }
}
