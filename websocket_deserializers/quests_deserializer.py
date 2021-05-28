from dataclasses import dataclass
from inspect import signature
from typing import List

@dataclass()
class questData:
    currentWaveNum: int
    currentQuestWaveMstId: int
    isRare: bool
    battleStatus: int
    result: bool
    continueCount: int

@dataclass()
class general:
    timestamp: int

@dataclass()
class guild:
    guildDataId: int
    comboCount: int
    comboCurrentUserId: int
    lethalArtCount: int

@dataclass()
class member:
    userId: int
    guildDataId: int
    modeType: int
    hp: int
    questSp: int
    maxHp: int
    questSpMax: int
    isNoDamage: bool
    isAi: bool
    isAuto: bool
    attackEffectLevel: int
    defenceEffectLevel: int
    magicAttackEffectLevel: int
    magicDefenceEffectLevel: int
    enemyTargetMemberRank: int
    ownTargetMemberRank: int

@dataclass()
class lethalArt:
    lethalArtMstId: int
    artCount: int
    successArtMstId: int
    failureArtMstId: int
    lethalArtMethodMstId: int
    status: int
    needCount: int
    startPreEffectTime: int
    startPrepareTime: int
    endPrepareTime: int
    winGuildDataId: int
    startTime: int
    endTime: int

@dataclass()
class art:
    artMstId: int
    guildDataId: int
    name: str
    startTime: int
    endTime: int
    initiator: int

@dataclass()
class historyInfluenceData:
    questHistoryId: int
    questData: questData
    general: general
    guilds: List[guild]
    members: List[member]
    lethalArt: lethalArt
    art: List[art]

@dataclass()
class userActInfluence:
    questHistoryId: int
    actionUserId: int
    actionGuildDataId: int
    receivedUserId: int
    receivedGuildDataId: int
    actionType: int
    usedSp: int
    cardMstId: int
    skillMstId: int
    attackType: int
    modeChange: int
    killed: int
    actionFlag: int
    actionValue: int

@dataclass()
class modeChangeMember:
    userId: int
    name: str
    guildDataId: int
    roleType: int
    memberRank: int
    hp: int
    questSp: int
    attack: int
    defence: int
    magicAttack: int
    magicDefence: int
    maxHp: int
    questEnemyMstId: int
    modeType: int
    maxModeChangeNum: int

@dataclass()
class userActRes:
    userActInfluence: List[userActInfluence]
    modeChangeMember: List[modeChangeMember]

@dataclass()
class artInfluence:
    artMstId: int
    guildDataId: int
    artActionFlag: int
    name: str
    startTime: int
    endTime: int
    questHistoryId: int
    actionUserId: int
    receivedUserId: int
    receivedGuildDataId: int
    actionFlag: int
    actionValue: int

@dataclass()
class startArtData:
    artInfluence: List[artInfluence]
    modeChangeMember: List[modeChangeMember]

@dataclass()
class lethalArtInfluence:
    artMstId: int
    guildDataId: int
    lethalArtActionFlag: int
    name: str
    startTime: int
    endTime: int
    questHistoryId: int
    actionUserId: int
    receivedUserId: int
    receivedGuildDataId: int
    actionFlag: int
    actionValue: int

@dataclass()
class startLethalArtData:
    lethalArtInfluence: List[lethalArtInfluence]
    modeChangeMember: List[modeChangeMember]

class QuestSystemScheduleInfo():

    def __init__(self, _list: list) -> None:
        self._list = _list
        self._index = iter(_list)
        self.historyInfluenceData = historyInfluenceData(0, 0, 0, [], [], 0, [])
        self.userActRes = userActRes([], [])
        self.startArtData = startArtData([], [])
        self.startLethalArtData = startLethalArtData([], [])
        self.deserialize_list()

    def read(self) -> int:
        return next(self._index)

    def check(self) -> bool:
        return self.read()

    def get_args(self, _class: type):
        return [self.read() for _ in range(len(signature(_class).parameters))]

    def deserialize_historyInfluence(self) -> None:
        if self.check():
            self.historyInfluenceData.questHistoryId = self.read()

            if self.check():
                self.historyInfluenceData.questData = questData(*self.get_args(questData))

            if self.check():
                self.historyInfluenceData.general = general(self.read())

            for _ in range(self.read()):
                if self.check():
                    self.historyInfluenceData.guilds.append(guild(*self.get_args(guild)))

            for _ in range(self.read()):
                if self.check():
                    self.historyInfluenceData.members.append(member(*self.get_args(member)))

            if self.check():
                self.historyInfluenceData.lethalArt = lethalArt(*self.get_args(lethalArt))

            for _ in range(self.check()):
                if self.check():
                    self.historyInfluenceData.art.append(art(*self.get_args(art)))

    def deserialize_userActRes(self) -> None:
        if self.check():
            for _ in range(self.read()):
                if self.check():
                    self.userActRes.userActInfluence.append(userActInfluence(*self.get_args(userActInfluence)))

            for _ in range(self.read()):
                if self.check():
                    self.userActRes.modeChangeMember.append(modeChangeMember(*self.get_args(modeChangeMember)))

    def deserialize_startArtData(self) -> None:
        if self.check():
            for _ in range(self.read()):
                if self.check():
                    self.startArtData.artInfluence.append(artInfluence(*self.get_args(artInfluence)))

            for _ in range(self.read()):
                if self.check():
                    self.startArtData.modeChangeMember.append(modeChangeMember(*self.get_args(modeChangeMember)))

    def deserialize_startLethalArtData(self) -> None:
        if self.check():
            for _ in range(self.read()):
                if self.check():
                    self.startArtData.artInfluence.append(lethalArtInfluence(*self.get_args(lethalArtInfluence)))

            for _ in range(self.read()):
                if self.check():
                    self.startArtData.modeChangeMember.append(modeChangeMember(*self.get_args(modeChangeMember)))

    def deserialize_list(self) -> None:
        if self.check():
            self.deserialize_historyInfluence()
            self.deserialize_userActRes()
            self.deserialize_startArtData()
            self.deserialize_startLethalArtData()